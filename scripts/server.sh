#!/bin/bash
source ./config.sh

INIT=49000
END=$(expr $INIT + $NUMTHREADS - 1)

rm -f _*.class
rm -f _*.java

cat /dev/null > serverlist
for i in $(seq $INIT $END); do 
    echo "localhost:"$i >> serverlist
done

for i in $(seq $INIT $END); do 
    $JAVA -jar ../pvesta/pvesta-server.jar $i &
done
