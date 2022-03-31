::: {.related role="navigation" aria-label="related navigation"}
### Navigation

-   [index](genindex.html "General Index")
-   [modules](py-modindex.html "Python Module Index") \|
-   [WikiTeam 0.3 documentation](#) »
:::

::: document
::: documentwrapper
::: bodywrapper
::: {.body role="main"}
::: {#welcome-to-wikiteam-s-documentation .section}
# Welcome to WikiTeam's documentation![¶](#welcome-to-wikiteam-s-documentation "Permalink to this headline"){.headerlink}

Contents:

::: {.toctree-wrapper .compound}
:::

[]{#module-dumpgenerator .target}

`dumpgenerator.`{.descclassname}`avoidWikimediaProjects`{.descname}[(]{.sig-paren}*config={}*, *other={}*[)]{.sig-paren}[¶](#dumpgenerator.avoidWikimediaProjects "Permalink to this definition"){.headerlink}

:   Skip Wikimedia projects and redirect to the dumps website

```{=html}
<!-- -->
```

`dumpgenerator.`{.descclassname}`bye`{.descname}[(]{.sig-paren}[)]{.sig-paren}[¶](#dumpgenerator.bye "Permalink to this definition"){.headerlink}

:   Closing message

```{=html}
<!-- -->
```

`dumpgenerator.`{.descclassname}`checkAPI`{.descname}[(]{.sig-paren}*api=None*, *session=None*[)]{.sig-paren}[¶](#dumpgenerator.checkAPI "Permalink to this definition"){.headerlink}

:   Checking API availability

```{=html}
<!-- -->
```

`dumpgenerator.`{.descclassname}`checkIndex`{.descname}[(]{.sig-paren}*index=None*, *cookies=None*, *session=None*[)]{.sig-paren}[¶](#dumpgenerator.checkIndex "Permalink to this definition"){.headerlink}

:   Checking index.php availability

```{=html}
<!-- -->
```

`dumpgenerator.`{.descclassname}`checkXMLIntegrity`{.descname}[(]{.sig-paren}*config={}*, *titles=\[\]*, *session=None*[)]{.sig-paren}[¶](#dumpgenerator.checkXMLIntegrity "Permalink to this definition"){.headerlink}

:   Check XML dump integrity, to detect broken XML chunks

```{=html}
<!-- -->
```

`dumpgenerator.`{.descclassname}`cleanHTML`{.descname}[(]{.sig-paren}*raw=\'\'*[)]{.sig-paren}[¶](#dumpgenerator.cleanHTML "Permalink to this definition"){.headerlink}

:   Extract only the real wiki content and remove rubbish

```{=html}
<!-- -->
```

`dumpgenerator.`{.descclassname}`cleanXML`{.descname}[(]{.sig-paren}*xml=\'\'*[)]{.sig-paren}[¶](#dumpgenerator.cleanXML "Permalink to this definition"){.headerlink}

:   Trim redundant info

```{=html}
<!-- -->
```

`dumpgenerator.`{.descclassname}`curateImageURL`{.descname}[(]{.sig-paren}*config={}*, *url=\'\'*[)]{.sig-paren}[¶](#dumpgenerator.curateImageURL "Permalink to this definition"){.headerlink}

:   Returns an absolute URL for an image, adding the domain if missing

```{=html}
<!-- -->
```

`dumpgenerator.`{.descclassname}`delay`{.descname}[(]{.sig-paren}*config={}*, *session=None*[)]{.sig-paren}[¶](#dumpgenerator.delay "Permalink to this definition"){.headerlink}

:   Add a delay if configured for that

```{=html}
<!-- -->
```

`dumpgenerator.`{.descclassname}`domain2prefix`{.descname}[(]{.sig-paren}*config={}*, *session=None*[)]{.sig-paren}[¶](#dumpgenerator.domain2prefix "Permalink to this definition"){.headerlink}

:   Convert domain name to a valid prefix filename.

```{=html}
<!-- -->
```

`dumpgenerator.`{.descclassname}`fixBOM`{.descname}[(]{.sig-paren}*request*[)]{.sig-paren}[¶](#dumpgenerator.fixBOM "Permalink to this definition"){.headerlink}

:   Strip Unicode BOM

```{=html}
<!-- -->
```

`dumpgenerator.`{.descclassname}`generateImageDump`{.descname}[(]{.sig-paren}*config={}*, *other={}*, *images=\[\]*, *start=\'\'*, *session=None*[)]{.sig-paren}[¶](#dumpgenerator.generateImageDump "Permalink to this definition"){.headerlink}

:   Save files and descriptions using a file list

```{=html}
<!-- -->
```

`dumpgenerator.`{.descclassname}`generateXMLDump`{.descname}[(]{.sig-paren}*config={}*, *titles=\[\]*, *start=None*, *session=None*[)]{.sig-paren}[¶](#dumpgenerator.generateXMLDump "Permalink to this definition"){.headerlink}

:   Generates a XML dump for a list of titles

```{=html}
<!-- -->
```

`dumpgenerator.`{.descclassname}`getImageNames`{.descname}[(]{.sig-paren}*config={}*, *session=None*[)]{.sig-paren}[¶](#dumpgenerator.getImageNames "Permalink to this definition"){.headerlink}

:   Get list of image names

```{=html}
<!-- -->
```

`dumpgenerator.`{.descclassname}`getImageNamesAPI`{.descname}[(]{.sig-paren}*config={}*, *session=None*[)]{.sig-paren}[¶](#dumpgenerator.getImageNamesAPI "Permalink to this definition"){.headerlink}

:   Retrieve file list: filename, url, uploader

```{=html}
<!-- -->
```

`dumpgenerator.`{.descclassname}`getImageNamesScraper`{.descname}[(]{.sig-paren}*config={}*, *session=None*[)]{.sig-paren}[¶](#dumpgenerator.getImageNamesScraper "Permalink to this definition"){.headerlink}

:   Retrieve file list: filename, url, uploader

```{=html}
<!-- -->
```

`dumpgenerator.`{.descclassname}`getJSON`{.descname}[(]{.sig-paren}*request*[)]{.sig-paren}[¶](#dumpgenerator.getJSON "Permalink to this definition"){.headerlink}

:   Strip Unicode BOM

```{=html}
<!-- -->
```

`dumpgenerator.`{.descclassname}`getNamespacesAPI`{.descname}[(]{.sig-paren}*config={}*, *session=None*[)]{.sig-paren}[¶](#dumpgenerator.getNamespacesAPI "Permalink to this definition"){.headerlink}

:   Uses the API to get the list of namespaces names and ids

```{=html}
<!-- -->
```

`dumpgenerator.`{.descclassname}`getNamespacesScraper`{.descname}[(]{.sig-paren}*config={}*, *session=None*[)]{.sig-paren}[¶](#dumpgenerator.getNamespacesScraper "Permalink to this definition"){.headerlink}

:   Hackishly gets the list of namespaces names and ids from the
    dropdown in the HTML of Special:AllPages

```{=html}
<!-- -->
```

`dumpgenerator.`{.descclassname}`getPageTitles`{.descname}[(]{.sig-paren}*config={}*, *session=None*[)]{.sig-paren}[¶](#dumpgenerator.getPageTitles "Permalink to this definition"){.headerlink}

:   Get list of page titles

```{=html}
<!-- -->
```

`dumpgenerator.`{.descclassname}`getPageTitlesAPI`{.descname}[(]{.sig-paren}*config={}*, *session=None*[)]{.sig-paren}[¶](#dumpgenerator.getPageTitlesAPI "Permalink to this definition"){.headerlink}

:   Uses the API to get the list of page titles

```{=html}
<!-- -->
```

`dumpgenerator.`{.descclassname}`getPageTitlesScraper`{.descname}[(]{.sig-paren}*config={}*, *session=None*[)]{.sig-paren}[¶](#dumpgenerator.getPageTitlesScraper "Permalink to this definition"){.headerlink}

:   Scrape the list of page titles from Special:Allpages

```{=html}
<!-- -->
```

`dumpgenerator.`{.descclassname}`getUserAgent`{.descname}[(]{.sig-paren}[)]{.sig-paren}[¶](#dumpgenerator.getUserAgent "Permalink to this definition"){.headerlink}

:   Return a cool user-agent to hide Python user-agent

```{=html}
<!-- -->
```

`dumpgenerator.`{.descclassname}`getWikiEngine`{.descname}[(]{.sig-paren}*url=\'\'*[)]{.sig-paren}[¶](#dumpgenerator.getWikiEngine "Permalink to this definition"){.headerlink}

:   Returns the wiki engine of a URL, if known

```{=html}
<!-- -->
```

`dumpgenerator.`{.descclassname}`getXMLFileDesc`{.descname}[(]{.sig-paren}*config={}*, *title=\'\'*, *session=None*[)]{.sig-paren}[¶](#dumpgenerator.getXMLFileDesc "Permalink to this definition"){.headerlink}

:   Get XML for image description page

```{=html}
<!-- -->
```

`dumpgenerator.`{.descclassname}`getXMLHeader`{.descname}[(]{.sig-paren}*config={}*, *session=None*[)]{.sig-paren}[¶](#dumpgenerator.getXMLHeader "Permalink to this definition"){.headerlink}

:   Retrieve a random page to extract XML headers (namespace info, etc)

```{=html}
<!-- -->
```

`dumpgenerator.`{.descclassname}`getXMLPage`{.descname}[(]{.sig-paren}*config={}*, *title=\'\'*, *verbose=True*, *session=None*[)]{.sig-paren}[¶](#dumpgenerator.getXMLPage "Permalink to this definition"){.headerlink}

:   Get the full history (or current only) of a page

```{=html}
<!-- -->
```

`dumpgenerator.`{.descclassname}`getXMLPageCore`{.descname}[(]{.sig-paren}*headers={}*, *params={}*, *config={}*, *session=None*[)]{.sig-paren}[¶](#dumpgenerator.getXMLPageCore "Permalink to this definition"){.headerlink}

:

```{=html}
<!-- -->
```

`dumpgenerator.`{.descclassname}`loadConfig`{.descname}[(]{.sig-paren}*config={}*, *configfilename=\'\'*[)]{.sig-paren}[¶](#dumpgenerator.loadConfig "Permalink to this definition"){.headerlink}

:   Load config file

```{=html}
<!-- -->
```

`dumpgenerator.`{.descclassname}`logerror`{.descname}[(]{.sig-paren}*config={}*, *text=\'\'*[)]{.sig-paren}[¶](#dumpgenerator.logerror "Permalink to this definition"){.headerlink}

:   Log error in file

```{=html}
<!-- -->
```

`dumpgenerator.`{.descclassname}`main`{.descname}[(]{.sig-paren}*params=\[\]*[)]{.sig-paren}[¶](#dumpgenerator.main "Permalink to this definition"){.headerlink}

:   Main function

```{=html}
<!-- -->
```

`dumpgenerator.`{.descclassname}`mwGetAPIAndIndex`{.descname}[(]{.sig-paren}*url=\'\'*[)]{.sig-paren}[¶](#dumpgenerator.mwGetAPIAndIndex "Permalink to this definition"){.headerlink}

:   Returns the MediaWiki API and Index.php

```{=html}
<!-- -->
```

`dumpgenerator.`{.descclassname}`readTitles`{.descname}[(]{.sig-paren}*config={}*, *start=None*[)]{.sig-paren}[¶](#dumpgenerator.readTitles "Permalink to this definition"){.headerlink}

:   Read title list from a file, from the title "start"

```{=html}
<!-- -->
```

`dumpgenerator.`{.descclassname}`removeIP`{.descname}[(]{.sig-paren}*raw=\'\'*[)]{.sig-paren}[¶](#dumpgenerator.removeIP "Permalink to this definition"){.headerlink}

:   Remove IP from HTML comments \<!-- -->

```{=html}
<!-- -->
```

`dumpgenerator.`{.descclassname}`reverse_readline`{.descname}[(]{.sig-paren}*filename*, *buf_size=8192*, *truncate=False*[)]{.sig-paren}[¶](#dumpgenerator.reverse_readline "Permalink to this definition"){.headerlink}

:   a generator that returns the lines of a file in reverse order

```{=html}
<!-- -->
```

`dumpgenerator.`{.descclassname}`saveConfig`{.descname}[(]{.sig-paren}*config={}*, *configfilename=\'\'*[)]{.sig-paren}[¶](#dumpgenerator.saveConfig "Permalink to this definition"){.headerlink}

:   Save config file

```{=html}
<!-- -->
```

`dumpgenerator.`{.descclassname}`saveImageNames`{.descname}[(]{.sig-paren}*config={}*, *images=\[\]*, *session=None*[)]{.sig-paren}[¶](#dumpgenerator.saveImageNames "Permalink to this definition"){.headerlink}

:   Save image list in a file, including filename, url and uploader

```{=html}
<!-- -->
```

`dumpgenerator.`{.descclassname}`saveIndexPHP`{.descname}[(]{.sig-paren}*config={}*, *session=None*[)]{.sig-paren}[¶](#dumpgenerator.saveIndexPHP "Permalink to this definition"){.headerlink}

:   Save index.php as .html, to preserve license details available at
    the botom of the page

```{=html}
<!-- -->
```

`dumpgenerator.`{.descclassname}`saveLogs`{.descname}[(]{.sig-paren}*config={}*, *session=None*[)]{.sig-paren}[¶](#dumpgenerator.saveLogs "Permalink to this definition"){.headerlink}

:   Save Special:Log

```{=html}
<!-- -->
```

`dumpgenerator.`{.descclassname}`saveSiteInfo`{.descname}[(]{.sig-paren}*config={}*, *session=None*[)]{.sig-paren}[¶](#dumpgenerator.saveSiteInfo "Permalink to this definition"){.headerlink}

:   Save a file with site info

```{=html}
<!-- -->
```

`dumpgenerator.`{.descclassname}`saveSpecialVersion`{.descname}[(]{.sig-paren}*config={}*, *session=None*[)]{.sig-paren}[¶](#dumpgenerator.saveSpecialVersion "Permalink to this definition"){.headerlink}

:   Save Special:Version as .html, to preserve extensions details

```{=html}
<!-- -->
```

`dumpgenerator.`{.descclassname}`truncateFilename`{.descname}[(]{.sig-paren}*other={}*, *filename=\'\'*[)]{.sig-paren}[¶](#dumpgenerator.truncateFilename "Permalink to this definition"){.headerlink}

:   Truncate filenames when downloading images with large filenames

```{=html}
<!-- -->
```

`dumpgenerator.`{.descclassname}`undoHTMLEntities`{.descname}[(]{.sig-paren}*text=\'\'*[)]{.sig-paren}[¶](#dumpgenerator.undoHTMLEntities "Permalink to this definition"){.headerlink}

:   Undo some HTML codes
:::

::: {#indices-and-tables .section}
# Indices and tables[¶](#indices-and-tables "Permalink to this headline"){.headerlink}

-   [[Index]{.std .std-ref}](genindex.html){.reference .internal}
-   [[Module Index]{.std .std-ref}](py-modindex.html){.reference
    .internal}
-   [[Search Page]{.std .std-ref}](search.html){.reference .internal}
:::
:::
:::
:::

::: {.sphinxsidebar role="navigation" aria-label="main navigation"}
::: sphinxsidebarwrapper
### [Table Of Contents](#)

-   [Welcome to WikiTeam's documentation!](#){.reference .internal}
-   [Indices and tables](#indices-and-tables){.reference .internal}

::: {role="note" aria-label="source link"}
### This Page

-   [Show Source](_sources/index.txt)
:::

::: {#searchbox style="display: none" role="search"}
### Quick search

<div>

</div>

<div>

</div>
:::
:::
:::

::: clearer
:::
:::

::: {.related role="navigation" aria-label="related navigation"}
### Navigation

-   [index](genindex.html "General Index")
-   [modules](py-modindex.html "Python Module Index") \|
-   [WikiTeam 0.3 documentation](#) »
:::

::: {.footer role="contentinfo"}
© Copyright 2016, WikiTeam developers. Created using
[Sphinx](http://sphinx-doc.org/) 1.4.5.
:::
