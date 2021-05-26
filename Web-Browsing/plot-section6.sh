#!/bin/bash

python scripts/objectnum-plt-energy-analysis.py #generate objectnum-plt-energy-relation.pdf for Figure 19.a
python scripts/pagesize-plt-energy-analysis.py #generate objectnum-plt-energy-relation.pdf for Figure 19.b
python scripts/draw-cdf.py # generate cdf-energy.pdf and cdf-plt.pdf for Figure 20
python scripts/energy-time-analysis.py #generate energy-plt-relation.pdf for Figure 21
python scripts/tree-generation-M1.py #generate tree-M1.png for Figure 22.a.
python scripts/tree-generation-M4.py #generate tree-M4.png for Figure 22.b.
python scripts/interface-selection.py #generate Table6.
echo "Success."