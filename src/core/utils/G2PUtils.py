#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2018 <boutin_arnaud@hotmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import sys

from g2p_seq2seq import data_utils
from g2p_seq2seq.g2p import G2PModel
import tensorflow as tf
from tensorflow.python.platform import flags
from core import PATH_G2P


FLAGS = tf.app.flags.FLAGS
FILES = ''

#MODEL = "/home/nono/Documents/Jarvis/workspace/topi_box/resources/fr/model_g2p_fr"

def interactive_(_):
    FLAGS.interactive = True
    FLAGS.model = "model_g2p_fr"
    main()

def decode_():
    FLAGS.decode = "/home/nono/workspace/topi_box/tmp/input_mots_to_gp2"
    FLAGS.output="/home/nono/workspace/topi_box/tmp/output_mots_to_gp2"
    FLAGS.model = PATH_G2P 
    main()

def evaluate_():
    FLAGS.evaluate = True
    FLAGS.model = "model_g2p_fr"
    main()

def train_():
    FLAGS.model = "model_g2p_fr"
    FLAGS.train = "/home/nono/workspace/topi_box/resources/model_vocal/frenchWords62K.dic"
    main()
    
def main():    
    """Main function.
      """
     
    if FLAGS.train:
        train_dic, valid_dic, test_dic =\
            data_utils.split_dictionary(FLAGS.train, FLAGS.valid, FLAGS.test)
        g2p_model = G2PModel(train_dic, valid_dic, test_dic)
        g2p_model.train()
    else:
        g2p_model = G2PModel(PATH_G2P)
        if FLAGS.decode:
            g2p_model.decode()
        elif FLAGS.interactive:
            g2p_model.interactive()
        elif FLAGS.evaluate:
            g2p_model.evaluate()
            
class  G2PTools():
    
    def run(self, main=None):
        f = flags.FLAGS
        f._parse_flags()
        main = main or sys.modules['__main__'].main
        main()

    def interactive(self) :
        self.run(interactive_)
    
    def train(self) :
        self.run(train_)
    
    def decode(self) :
        self.run(decode_)

if __name__ == "__main__":
    tool = G2PTools()
    tool.decode()
