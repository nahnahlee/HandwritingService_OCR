# funit_model.py (updated: remove internal backward calls + half-precision norm buffers)
import copy

import torch
import torch.nn as nn

from networks import FewShotGen, GPPatchMcResDis


def recon_criterion(predict, target):
    return torch.mean(torch.abs(predict - target))

class FUNITModel(nn.Module):
    def __init__(self, hp):
        super(FUNITModel, self).__init__()
        self.gen = FewShotGen(hp['gen'])
        self.dis = GPPatchMcResDis(hp['dis'])
        self.gen_test = copy.deepcopy(self.gen)

        # Cast normalization buffers and affine params to half precision for AMP
        for m in self.modules():
            if hasattr(m, 'running_mean') and isinstance(m.running_mean, torch.Tensor):
                m.running_mean.data = m.running_mean.data.half()
            if hasattr(m, 'running_var') and isinstance(m.running_var, torch.Tensor):
                m.running_var.data = m.running_var.data.half()
            if hasattr(m, 'weight') and isinstance(m.weight, torch.Tensor):
                m.weight.data = m.weight.data.half()
            if hasattr(m, 'bias') and isinstance(m.bias, torch.Tensor):
                m.bias.data = m.bias.data.half()

    def forward(self, co_data, cl_data, hp, mode):
        xa, la = co_data[0].cuda(), co_data[1].cuda()
        xb, lb = cl_data[0].cuda(), cl_data[1].cuda()

        if mode == 'gen_update':
            c_xa = self.gen.enc_content(xa)
            s_xa = self.gen.enc_class_model(xa)
            s_xb = self.gen.enc_class_model(xb)
            xt = self.gen.decode(c_xa, s_xb)
            xr = self.gen.decode(c_xa, s_xa)
            l_adv_t, gacc_t, xt_feat = self.dis.calc_gen_loss(xt, lb)
            l_adv_r, gacc_r, xr_feat = self.dis.calc_gen_loss(xr, la)
            _, xb_feat = self.dis(xb, lb)
            _, xa_feat = self.dis(xa, la)
            l_c_rec = recon_criterion(
                xr_feat.mean((2, 3)), xa_feat.mean((2, 3))
            )
            l_m_rec = recon_criterion(
                xt_feat.mean((2, 3)), xb_feat.mean((2, 3))
            )
            l_x_rec = recon_criterion(xr, xa)
            l_adv = 0.5 * (l_adv_t + l_adv_r)
            acc = 0.5 * (gacc_t + gacc_r)
            l_total = (
                hp['gan_w'] * l_adv +
                hp['r_w']   * l_x_rec +
                hp['fm_w']  * (l_c_rec + l_m_rec)
            )
            return l_total, l_adv, l_x_rec, l_c_rec, l_m_rec, acc

        elif mode == 'dis_update':
            xb.requires_grad_(True)
            l_real_p, acc_r, resp_r = self.dis.calc_dis_real_loss(xb, lb)
            fake_img = self.gen.decode(
                self.gen.enc_content(xa).detach(),
                self.gen.enc_class_model(xb)
            ).detach()
            l_fake_p, acc_f, _ = self.dis.calc_dis_fake_loss(fake_img, lb)
            l_reg_p = self.dis.calc_grad2(resp_r, xb)
            l_real = hp['gan_w'] * l_real_p
            l_fake = hp['gan_w'] * l_fake_p
            l_reg  = 10 * l_reg_p
            l_total = l_real + l_fake + l_reg
            acc = 0.5 * (acc_f + acc_r)
            return l_total, l_fake_p, l_real_p, l_reg_p, acc

        else:
            raise ValueError('Unsupported mode: ' + str(mode))

    def test(self, co_data, cl_data):
        self.eval()
        xa = co_data[0].cuda()
        xb = cl_data[0].cuda()
        c_xa_current = self.gen.enc_content(xa)
        s_xa_current = self.gen.enc_class_model(xa)
        s_xb_current = self.gen.enc_class_model(xb)
        xt_current = self.gen.decode(c_xa_current, s_xb_current)
        xr_current = self.gen.decode(c_xa_current, s_xa_current)
        c_xa = self.gen_test.enc_content(xa)
        s_xa = self.gen_test.enc_class_model(xa)
        s_xb = self.gen_test.enc_class_model(xb)
        xt = self.gen_test.decode(c_xa, s_xb)
        xr = self.gen_test.decode(c_xa, s_xa)
        self.train()
        return xa, xr_current, xt_current, xb, xr, xt
