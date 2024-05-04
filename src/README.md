The filesystem should have the following structure.

```
/checksums.txt
/data/
```

The format for checksums.txt should be a list of MD5 hashes and escaped
absolute paths terminated by newlines.

```
<MD5 hash> /escaped/path/to/file
```

Here is an example.

```
67c5023dcaa5d8402020a586e3c5b1a4 /Xv6 System Call Statistics.latex
10f6196729931f7ffffeaa2de0a5ae3c /Xv6 System Call Statistics.pdf
83ff80f72d10d2e192a54a5a4c45c322 /scstats-dump.tgz
00bf48fe3c1357250eb3241d3f34c5d4 /scstats-screenshot.png
746308829575e17c3331bbcb00c0898b /name-with-back-\\-slash.txt
95903fa198fa3e466796a48fd02eb611 /name-with-new-\n-line.txt
```
