#!/bin/bash
################################################################################
# File:    build_docs_and_redoc.sh
# Purpose: Script that builds ReDoc and Sphinx docs and updates GitHub Pages.
# Authors: Michael Altfield <michael@michaelaltfield.net>, Sara Zanzottera
# Created: 2020-07-17
# Updated: 2021-07-29
# Version: 0.2
################################################################################
 
###################
# INSTALL DEPENDS #
###################
 
apt-get update
apt-get -y install git rsync python3-sphinx python3-sphinx-rtd-theme
 
#####################
# DECLARE VARIABLES #
#####################
 
pwd
ls -lah
export SOURCE_DATE_EPOCH=$(git log -1 --pretty=%ct)
 
##############
# BUILD DOCS #
##############
 
make -C docs clean
make -C docs html
 
mkdir redoc
cd redoc
generate-redoc
cd ../

#######################
# Update GitHub Pages #
#######################
 
git config --global user.name "${GITHUB_ACTOR}"
git config --global user.email "${GITHUB_ACTOR}@users.noreply.github.com"
 
docroot=`mktemp -d`
rsync -av "docs/build/html/" "${docroot}/"
rsync -av "redoc/" "${docroot}/"
 
pushd "${docroot}"
 
# don't bother maintaining history; just generate fresh
git init
git remote add deploy "https://token:${GITHUB_TOKEN}@github.com/${GITHUB_REPOSITORY}.git"
git checkout -b gh-pages
 
# add .nojekyll to the root so that github won't 404 on content added to dirs
# that start with an underscore (_), such as our "_content" dir..
touch .nojekyll
 
# Add README
cat > README.md <<EOF

# flashcards-api - Internal Documentation Build Artifacts

Nothing to see here. The content of this branch is essentially a cache for build artifacts.

If you are looking for the documentation, check the relevant development branch's 'docs/' directory or
go to https://ebisu-flashcards.github.io/flashcards-core/ .

EOF
 
# copy the resulting html pages built from sphinx above to our new git repo
git add .
 
# commit all the new files
msg="Updating Docs and ReDoc for commit ${GITHUB_SHA} made on `date -d"@${SOURCE_DATE_EPOCH}" --iso-8601=seconds` from ${GITHUB_REF} by ${GITHUB_ACTOR}"
git commit -am "${msg}"
 
# overwrite the contents of the gh-pages branch on our github.com repo
git push deploy gh-pages --force
 
popd # return to main repo sandbox root
