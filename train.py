#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
@author: Qun Yang
@license: (C) Copyright 2021, University of Auckland
@contact: qyan327@aucklanduni.ac.nz
@date: 7/02/21 11:03 AM
@description:  
@version: 1.0
"""


import torch
from torch.utils.data import DataLoader
from torch import nn, optim
import numpy as np
import data_processing as dp
import time
import json
import argparse
from models.Generator import Generator
from models.Discriminator import Discriminator


data_path = './data/data_processed'
save_path = './results'


class BaseExperiment:

    def __init__(self, args):
        self.args = args
        torch.manual_seed(self.args.seed)
        np.random.seed(self.args.seed)
        print('> Training arguments:')
        for arg in vars(args):
            print('>>> {}: {}'.format(arg, getattr(args, arg)))
        white_noise = dp.DatasetReader(white_noise=self.args.dataset,
                                       data_path=data_path,
                                       len_seg=self.args.len_seg
                                       )
        self.data_loader = DataLoader(dataset=white_noise.dataset,
                                      batch_size=args.batch_size,
                                      shuffle=True
                                      )
        self.Generator = Generator(args)  # Generator
        self.Discriminator = Discriminator(args)  # Discriminator

    def select_optimizer(self, model):
        if self.args.optimizer == 'Adam':
            optimizer = optim.Adam(filter(lambda p: p.requires_grad, model.parameters()),
                                   lr=self.args.learning_rate,
                                   betas=(0.5, 0.9)
                                   )
        elif self.args.optimizer == 'RMS':
            optimizer = optim.RMSprop(filter(lambda p: p.requires_grad, model.parameters()),
                                      lr=self.args.learning_rate
                                      )
        elif self.args.optimizer == 'SGD':
            optimizer = optim.SGD(filter(lambda p: p.requires_grad, model.parameters()),
                                  lr=self.args.learning_rate,
                                  momentum=0.9
                                  )
        elif self.args.optimizer == 'Adagrad':
            optimizer = optim.Adagrad(filter(lambda p: p.requires_grad, model.parameters()),
                                      lr=self.args.learning_rate
                                      )
        elif self.args.optimizer == 'Adadelta':
            optimizer = optim.Adadelta(filter(lambda p: p.requires_grad, model.parameters()),
                                       lr=self.args.learning_rate
                                       )
        return optimizer

    def weights_init(self, model):
        initializers = {'xavier_uniform_': nn.init.xavier_uniform_,
                        'xavier_normal_': nn.init.xavier_normal,
                        'orthogonal_': nn.init.orthogonal_,
                        'kaiming_normal_': nn.init.kaiming_normal_
                        }
        if isinstance(model, nn.Linear):
            initializer = initializers[self.args.initializer]
            initializer(model.weight)
            model.bias.data.fill_(0)

    def file_name(self):
        return '{}_{}_{}_{}_{}_{}'.format(self.args.model_name,
                                          self.args.net_name,
                                          self.args.len_seg,
                                          self.args.optimizer,
                                          self.args.learning_rate,
                                          self.args.num_epoch
                                          )

    def gradient_penalty(self):
        pass

    def train(self):
        self.Generator.apply(self.weights_init)
        self.Discriminator.apply(self.weights_init)
        gen_optimizer = self.select_optimizer(self.Generator)
        dis_optimizer = self.select_optimizer(self.Generator)
        losses = {}
        dis_losses, gen_losses = [0], [0]
        for epoch in range(self.args.num_epoch):
            t0 = time.time()
            # Train Discriminator for k steps
            for _ in range(5):
                for _, sample_batched in enumerate(self.data_loader):
                    pred_real = self.Discriminator(torch.tensor(sample_batched, dtype=torch.float32))
                    loss_real = - pred_real.mean()
                    # Generate data
                    z = torch.rand(self.args.batch_size, self.args.dim_noise)
                    x_fake = self.Generator(z).detach()
                    pred_fake = self.Discriminator(x_fake)
                    loss_fake = pred_fake.mean()
                    # Discriminator loss
                    dis_loss = loss_real + loss_fake
                    dis_optimizer.zero_grad()
                    dis_loss.backward()
                    dis_optimizer.step()
            # Train Generator
            z = torch.rand(self.args.batch_size, self.args.dim_noise)
            x_fake = self.Generator(z)
            pred_fake = self.Discriminator(x_fake)
            gen_loss = - pred_fake.mean()
            gen_optimizer.zero_grad()
            gen_loss.backward()
            gen_optimizer.step()
            t1 = time.time()
            print('\033[1;31m[Epoch {:>4}]\033[0m  '
                  '\033[1;31mDiscriminator loss = {:.5f}\033[0m  '
                  '\033[1;32mGenerator loss = {:.5f}\033[0m  '
                  'Time cost={:.2f}s'.format(epoch + 1,
                                             dis_loss.item(),
                                             - gen_loss.item(),
                                             t1 - t0)
                  )
            dis_losses.append(dis_loss.item())
            gen_losses.append(- gen_loss.item())
        # Save models
        path_gen = '{}/models/{}_Gen.model'.format(save_path, self.file_name())
        path_dis = '{}/models/{}_Dis.model'.format(save_path, self.file_name())
        torch.save(self.Generator.state_dict(), path_gen)
        torch.save(self.Discriminator.state_dict(), path_dis)
        # Write learning history
        losses['Discriminator'] = dis_losses
        losses['Generator'] = gen_losses
        losses = json.dumps(losses, indent=2)
        with open('{}/learning history/{}.json'.format(save_path, self.file_name()), 'w') as f:
            f.write(losses)


def main():
    # Hyper-parameters
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', default='W-1', type=str)
    parser.add_argument('--model_name', default='GAN', type=str)
    parser.add_argument('--net_name', default='MLP', type=str)
    parser.add_argument('--len_seg', default=400, type=int)
    parser.add_argument('--optimizer', default='SGD', type=str)
    parser.add_argument('--initializer', default='xavier_uniform_', type=str)
    parser.add_argument('--dim_noise', default=50, type=int)
    parser.add_argument('--dim_input', default=384, type=int)
    parser.add_argument('--dim_hidden', default=1000, type=int)
    parser.add_argument('--dim_output', default=384, type=int)
    parser.add_argument('--seed', default=1993, type=int)
    parser.add_argument('--batch_size', default=16, type=int)
    parser.add_argument('--num_epoch', default=100, type=int)
    parser.add_argument('--learning_rate', default=1e-2, type=float)
    args = parser.parse_args()
    exp = BaseExperiment(args)
    exp.train()


if __name__ == '__main__':
    main()
