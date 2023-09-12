FROM ubuntu:22.04

MAINTAINER muditha dantanarayana <muditha.danta@gmail.com>

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
	wget git \
	g++ gfortran \
	autoconf libtool automake flex bison \
	cmake make \
	python3-dev python3-pip git-core vim \
	zlib1g \
	build-essential libhdf5-serial-dev \
	libnetcdf-dev libnetcdff-dev \
	libopenjp2-7-dev libpng-dev libjpeg8-dev \
	libeccodes-dev \
	jasper

#	language-pack-en openssh-server vim software-properties-common \
#	pandoc python3-setuptools imagemagick\
#	libfreetype6-dev \
#	libeccodes0 libeccodes-data libeccodes-dev \
#	python3-numpy python3-mysqldb python3-scipy python3-sphinx \
#	libedit-dev \
#	libproj-dev libgdal-dev gdal-bin
#	apt-utils binutils unzip
#	gcc

#Paper reference 2.7.3
RUN mkdir source_builds && cd source_builds && mkdir eccodes && cd eccodes \
	&& wget https://confluence.ecmwf.int/download/attachments/45757960/eccodes-2.27.0-Source.tar.gz?api=v2 \
	&& tar -xzf eccodes-2.27.0-Source.tar.gz?api=v2 \
	&& mkdir build && cd build \
	&& cmake -DCMAKE_INSTALL_PREFIX=/usr/ ../eccodes-2.27.0-Source \
	&& make && make install

RUN mkdir flex_src && cd /flex_src \
	&& git clone https://www.flexpart.eu/gitmob/flexpart --branch dev --single-branch \
	&& cd flexpart/src \
	&& cp makefile makefile_local \
	&& sed -i '74a INCPATH1 = /usr/include\nINCPATH2 = /usr/include\nLIBPATH1 = /usr/lib\nF90 = gfortran' makefile_local \
	&& sed -i 's/LIBS = -lgrib_api_f90 -lgrib_api -lm -ljasper $(NCOPT)/LIBS = -leccodes_f90 -leccodes -lm -ljasper $(NCOPT)/' makefile_local \
	&& make -f makefile_local

ENV PATH /flex_src/flexpart/src/:$PATH

#RUN FLEXPART
