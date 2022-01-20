#!/bin/bash
source ./config.sh
$JAVA -jar ../pvesta/pvesta-client.jar -l serverlist -m ../examples/brake-system.maude -f formula.quatex -d1 0.01
