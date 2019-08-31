function version_gt() { 
    test "$(printf '%s\n' "$@" | sort -V | head -n 1)" != "$1"
}

LAST_RELEASE=`git describe origin/master | cut -c2-`
CURRENT_VERSION=`grep -F __version__ instabot/__init__.py | awk -F "'" '{print $2}'`

echo "LAST_RELEASE ${LAST_RELEASE}"
echo "CURRENT_VERSION ${CURRENT_VERSION}"

if version_gt $CURRENT_VERSION $LAST_RELEASE
then
    echo "Version increased!"
    git config --global user.email "bot@github.com"
    git config --global user.name "Github Bot"
    git tag -a v$CURRENT_VERSION
    # git remote remove origin
    # git remote add origin https://${GITHUB_TOKEN}@github.com/ailinykh/instabot.git
    git push origin --tags HEAD
else
    echo "Current version not greater than release"
fi