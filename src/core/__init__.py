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

import os

"""
    Paramètres par defaut 
"""
LANG = 'fr'

"""
    Path
"""
CURRENT_DIR     = os.path.dirname(__file__)
PATH_RESOURCES  = os.path.join(CURRENT_DIR, "..", "..", "resources")
PATH_VOCAL      = os.path.join(PATH_RESOURCES, LANG, "model_vocal")
PATH_TTS        = os.path.join(PATH_RESOURCES, LANG, "tts")
PATH_G2P        = os.path.join(PATH_RESOURCES, LANG, "g2p")

"""
    Paranètre de la base de données
"""
#HOST_DB   = "192.168.1.100"
HOST_DB   = "127.0.0.1"
PORT_DB   = 3306
USER_DB   = "kodi"
PASSWD_DB = "kodi"
DB_DB     = "topibox"


"""
    Range du scan des adresses IP du reseau et des ports
"""
IP_MIN_SCAN      = 1
IP_MAX_SCAN      = 200

SCAN_PORT_ENABLE = False
PORT_MIN_SCAN    = 1
PORT_MAX_SCAN    = 10025

"""
    Ports
"""
#Ports applicatifs
PORT_SERVER                 = 7002
PORT_HTTP_KODI              = 8081
PORT_WS_KODI                = 9090

#Ports de controle, de stream, d'échange 
# Fixe car ces port sont utilisés avec Topibox comme client
PORT_CONTROL_SAT_CONNECT    = 50000
PORT_TTS                    = 50001
PORT_STREAM_MUSIC           = 50002

# pas Fixe car ces port sont utilisés avec Topibox comme serveur
PORT_BASE                       = 50000
PORT_ADD                        = 1000    
PORT_VOCAL_ADD                  = 1
PORT_VOCAL_SENDER_ADD           = 1
PORT_VOCAL_RECEIVER_ADD         = 2
PORT_UPDATE_FILES_ADD           = 5

"""
    Fichiers de paramétrage 
"""

#PATH_RESOURCES      = "../../resources/"
PLAYLIST_PREFIX         = "playlist_"
MAPPING_FILE            = "serieMapping.json"
MODEL_PHRASE_BASE_FILE  = "model_base.txt"


"""
    Fichiers du modele vocal 
"""

KEYPHRASE                           = "keyphrase.list"
MODEL_LM_VOCAL                      = "custom.lm.bin" 
DICTIONARY                          = "custom.dic"  
ACOUSTIC                            = "acoustic" 
ACOUSTIC_MODEL_README               = os.path.join(ACOUSTIC, "README")
ACOUSTIC_MODEL_LICENSE              = os.path.join(ACOUSTIC, "LICENSE")
ACOUSTIC_MODEL_FEAT_PARAMS          = os.path.join(ACOUSTIC, "feat.params")
ACOUSTIC_MODEL_MDEF                 = os.path.join(ACOUSTIC, "mdef")
ACOUSTIC_MODEL_MEANS                = os.path.join(ACOUSTIC, "means")
ACOUSTIC_MODEL_MIXTURE_WEIGHTS      = os.path.join(ACOUSTIC, "mixture_weights")
ACOUSTIC_MODEL_NOISEDICT            = os.path.join(ACOUSTIC, "noisedict")
#ACOUSTIC_MODEL_SENDUMP              = os.path.join(ACOUSTIC, "acoustic/sendump")
ACOUSTIC_MODEL_TRANSITION_MATRICES  = os.path.join(ACOUSTIC, "transition_matrices")
ACOUSTIC_MODEL_VARIANCES            = os.path.join(ACOUSTIC, "variances")

"""
    Outil du model 
"""

NGRAM_COUNT = "ngram-count"


