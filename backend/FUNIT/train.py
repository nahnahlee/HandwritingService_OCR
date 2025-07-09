import torch
import os
import sys
import argparse
import shutil

from torch.cuda.amp import autocast, GradScaler
scaler = GradScaler()

import torch.backends.cudnn as cudnn
cudnn.benchmark = True

from tensorboardX import SummaryWriter

from utils import get_config, get_train_loaders, make_result_folders
from utils import write_loss, write_html, write_1images, Timer
from trainer import Trainer

# Argument parsing
tParser = argparse.ArgumentParser()
parser = argparse.ArgumentParser()
parser.add_argument('--config', type=str, default='configs/funit_animals.yaml', help='configuration file for training and testing')
parser.add_argument('--output_path', type=str, default='.', help='outputs path')
parser.add_argument('--multigpus', action='store_true')
parser.add_argument('--batch_size', type=int, default=0)
parser.add_argument('--test_batch_size', type=int, default=4)
parser.add_argument('--resume', action='store_true')
opts = parser.parse_args()

# Load experiment setting
config = get_config(opts.config)
max_iter = config.get('max_iter', 0)
# Override the batch size if specified.
if opts.batch_size != 0:
    config['batch_size'] = opts.batch_size

# Initialize trainer and model
trainer = Trainer(config)
trainer.cuda()
if opts.multigpus:
    ngpus = torch.cuda.device_count()
    config['gpus'] = ngpus
    print(f"Number of GPUs: {ngpus}")
    trainer.model = torch.nn.DataParallel(trainer.model, device_ids=list(range(ngpus)))
else:
    config['gpus'] = 1

# Get data loaders
loaders = get_train_loaders(config)
train_content_loader, train_class_loader, test_content_loader, test_class_loader = loaders

# Setup logger and output folders
model_name = os.path.splitext(os.path.basename(opts.config))[0]
train_writer = SummaryWriter(os.path.join(opts.output_path, "logs", model_name))
output_directory = os.path.join(opts.output_path, "outputs", model_name)
checkpoint_directory, image_directory = make_result_folders(output_directory)
shutil.copy(opts.config, os.path.join(output_directory, 'config.yaml'))

# Start iterations
iterations = 0
if opts.resume:
    # Implement resume logic here if needed
    pass

while True:
    for it, (co_data, cl_data) in enumerate(zip(train_content_loader, train_class_loader)):
        with Timer("Elapsed time in update: %f"):
            # --- Discriminator update with AMP ---
            trainer.dis_opt.zero_grad()
            with autocast():
                l_total_d, l_fake_p, l_real_pre, l_reg_pre, d_acc = trainer.model(
                    co_data, cl_data, config, 'dis_update'
                )
            scaler.step(trainer.dis_opt)
            scaler.update()

            # --- Generator update with AMP ---
            trainer.gen_opt.zero_grad()
            with autocast():
                l_total_g, l_adv, l_x_rec, l_c_rec, l_m_rec, g_acc = trainer.model(
                    co_data, cl_data, config, 'gen_update'
                )
            scaler.step(trainer.gen_opt)
            scaler.update()

            torch.cuda.synchronize()
            print(f'D acc: {d_acc:.4f}\t G acc: {g_acc:.4f}')

        # Logging losses
        if (iterations + 1) % config.get('log_iter', 100) == 0:
            print(f"Iteration: {iterations + 1:08d}/{max_iter:08d}")
            write_loss(iterations, trainer, train_writer)

        # Save/display images periodically
        if ((iterations + 1) % config.get('image_save_iter', 1000) == 0 or
            (iterations + 1) % config.get('image_display_iter', 100) == 0):
            key_str = (
                f"{iterations + 1:08d}" 
                if (iterations + 1) % config.get('image_save_iter', 1000) == 0
                else 'current'
            )
            if key_str != 'current':
                write_html(
                    os.path.join(output_directory, "index.html"),
                    iterations + 1,
                    config['image_save_iter'],
                    'images'
                )
            with torch.no_grad():
                # Training images
                for t, (val_co, val_cl) in enumerate(zip(train_content_loader, train_class_loader)):
                    if t >= opts.test_batch_size:
                        break
                    outputs = trainer.test(val_co, val_cl, opts.multigpus)
                    write_1images(outputs, image_directory, f'train_{key_str}_{t:02d}')
                # Testing images
                for t, (test_co, test_cl) in enumerate(zip(test_content_loader, test_class_loader)):
                    if t >= opts.test_batch_size:
                        break
                    outputs = trainer.test(test_co, test_cl, opts.multigpus)
                    write_1images(outputs, image_directory, f'test_{key_str}_{t:02d}')

        # Save checkpoints periodically
        if (iterations + 1) % config.get('snapshot_save_iter', 5000) == 0:
            trainer.save(checkpoint_directory, iterations, opts.multigpus)
            print(f'Saved model at iteration {iterations + 1}')

        iterations += 1
        if iterations >= max_iter:
            print("Finish Training")
            sys.exit(0)
