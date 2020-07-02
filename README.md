# Make Standalone Release Tarballs of Geckodriver

This script builds a stand-alone tarball of gecko-driver. It's a bit like
`cargo vendor`, but it only vendors local dependencies (those with relative
path overrides in Cargo.toml).

Run it from in [the geckodriver directory within the Mozilla
mono-repo](https://hg.mozilla.org/mozilla-unified/file/tip/testing/geckodriver).

At the moment it only vendors direct dependencies of geckodriver. For now that
is all that is required.
