#!/bin/bash
set +e
cd ~/

echo "------ Remove old joid repo ------"
rm -rf joid

echo "------ Git clone repo ------"
git clone http://gerrit.opnfv.org/gerrit/joid.git
