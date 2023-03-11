#!/bin/bash

#pushd /g/g15/bolet1/workspace/benchmarks/rodinia/rodinia_3.1/openmp/cfd
#echo "Doing CFD runs..."
#for i in {1..10}
#do
#	./euler3d_cpu ../../data/cfd/missile.domn.0.2M | grep -ni "Compute time"
#done
#
#popd

# Let's do the runs for SP and FT
pushd /g/g15/bolet1/workspace/benchmarks/NPB/SNU_NPB_2019/NPB3.3-OMP-C/bin
echo "Doing FT runs..."
for i in {1..10}
do
	./ft.C.x | grep -ni "Time in seconds"
done

#echo "Doing SP runs..."
#for i in {1..10}
#do
#	./sp.C.x | grep -ni "Time in seconds"
#done

popd

