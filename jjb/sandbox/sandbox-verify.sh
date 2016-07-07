#!/bin/bash

# this is where we check the commit message, unit test, etc.
cd $WORKSPACE
echo
echo "Commit Message is"
echo "-------------------------------------"
git log --format=%B -n 1 $(git rev-parse HEAD)
echo "-------------------------------------"
echo
echo "Repo contents"
echo "-------------------------------------"
ls -al
echo "-------------------------------------"
echo
echo "Changed files are"
echo "-------------------------------------"
git diff origin/master --name-only
echo "-------------------------------------"
echo
echo "Change introduced"
echo "-------------------------------------"
git diff origin/master
echo "-------------------------------------"
echo
echo "git show"
echo "-------------------------------------"
git show
echo "-------------------------------------"
