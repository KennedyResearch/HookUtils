#!/bin/sh

old_path="$1"
old_row="$2"
new_path="$3"
new_row="$4"

old_directory="/projectnb/trenders/0$10$2_test/scripts"
new_directory= "/projectnb/trenders/0$30$4_test/scripts"

echo "Moving scripts..."
mkdir $new_directory
cp old_directory/* new_directory

echo "Cleaning up..."
rm $new_directory/*.e* 
rm $new_directory/*.o*

echo "Changing path-row settings..."
rename $old_path $new_path $new_directory/*$old_path*
rename $old_row $new_row $new_directory/*$old_row*
find $new_directory/scripts -type f -exec sed -i 's/$old_path/$new_path/g' {} \;
find $new_directory/scripts -type f -exec sed -i 's/$old_row/$new_row/g' {} \;

echo "Done!"
