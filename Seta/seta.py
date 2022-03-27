# -*- coding:utf-8 -*-

from SetaCore import Seta, SETA_SOC
import sys
import colorama

colorama.init(autoreset=False)

if sys.argv.__len__() != 2:
    print('\033[31mERROR: no source file.\033[0m')
    sys.exit(1)

seta = Seta(sys.argv[1], SETA_SOC)
seta.run()
