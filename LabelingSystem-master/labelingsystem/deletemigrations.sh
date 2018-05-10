for D in `find . -maxdepth 1 -type d`
do
    rm -rf ./${D}/migrations
done