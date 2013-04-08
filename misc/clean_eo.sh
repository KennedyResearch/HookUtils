#!/bin/csh

if ( ! -d "eo" ) then
	echo "Creating directory 'eo' for .e and .o files"
	mkdir "eo"
	
endif

mv ./*.e* ./eo
mv ./*.o* ./eo

echo "Done!"
