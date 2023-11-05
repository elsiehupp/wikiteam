# `MediaWiki Dump Generator`

**MediaWiki Dump Generator can archive wikis from the largest to the tiniest.**

`MediaWiki Dump Generator` is an ongoing project to port the legacy [`wikiteam`](https://github.com/WikiTeam/wikiteam) toolset to Python 3 and PyPI to make it more accessible for today's archivers.

Most of the focus has been on the core `dumpgenerator` tool. Python 3 versions of the other `wikiteam` tools may be added over time.

## MediaWiki Dump Generator Toolset

MediaWiki Dump Generator is a set of tools for archiving wikis. The main general-purpose module of MediaWiki Dump Generator is dumpgenerator, which can download XML dumps of MediaWiki sites that can then be parsed or redeployed elsewhere.

Wikipedia is far too large to manage the dump easily and [dumps are already freely available](https://en.wikipedia.org/wiki/Wikipedia:Database_download#Where_do_I_get_the_dumps?).

## Installing the tools

For prerequisites and installation see [Installation](./INSTALLATION.md)

## Using the tools

### Work-in-Progress
The launcher script is currently under development and does not function as documented.

For usage see [Usage](./USAGE.md)

## Types of dump

There are two types of backups that can be made XML dumps (current and history) and image dumps. Both can be done in one dump.

An XML dump contains the meta-data of the edits (author, date, comment) and the wikitext. An XML dump may be "current" or "history". A "history" dump contains the complete history of every page, which is better for CC-BY-SA licencing and is the default. A "current" dump contains only the last edit for every page.

An image dump contains all the images available in a wiki, plus their descriptions.

## Publishing the dump

Please consider publishing your wiki dump(s). You can do it yourself as explained in [Publishing](./PUBLISHING.md).

## Getting help

* You can read and post in MediaWiki Client Tools' [GitHub Discussions]( https://github.com/orgs/mediawiki-client-tools/discussions).
* If you need help (other than reporting a bug), you can reach out on MediaWiki Client Tools' [Discussions/Q&A](https://github.com/orgs/mediawiki-client-tools/discussions/categories/q-a).

## Contributing

For information on reporting bugs and proposing changes, please see the [Contributing](./CONTRIBUTING.md) guide.

### Further info for developers

* [MediaWiki Action API](https://www.mediawiki.org/wiki/API:Main_page)
* [The Internet Archive Python Library](https://archive.org/developers/internetarchive/)

## Code of Conduct

`mediawiki-client-tools` has a [Code of Conduct](./CODE_OF_CONDUCT.md).

At the moment the only person responsible for reviewing CoC reports is the repository administrator, Elsie Hupp, but we will work towards implementing a broader-based approach to reviews.

You can contact Elsie Hupp directly via email at [mediawiki-client-tools@elsiehupp.com](mailto:mediawiki-client-tools@elsiehupp.com) or on Matrix at [@elsiehupp:beeper.com](https://matrix.to/#/@elsiehupp:beeper.com). (Please state up front if your message concerns the Code of Conduct, as these messages are confidential.)

## Contributors

**WikiTeam** is the [Archive Team](http://www.archiveteam.org) [[GitHub](https://github.com/ArchiveTeam)] subcommittee on wikis.
It was founded and originally developed by [Emilio J. Rodríguez-Posada](https://github.com/emijrp), a Wikipedia veteran editor and amateur archivist. Thanks to people who have helped, especially to: [Federico Leva](https://github.com/nemobis), [Alex Buie](https://github.com/ab2525), [Scott Boyd](http://www.sdboyd56.com), [Hydriz](https://github.com/Hydriz), Platonides, Ian McEwen, [Mike Dupont](https://github.com/h4ck3rm1k3), [balr0g](https://github.com/balr0g) and [PiRSquared17](https://github.com/PiRSquared17).

**MediaWiki Dump Generator**
The Python 3 initiative is currently being led by [Elsie Hupp](https://github.com/elsiehupp), with contributions from [Victor Gambier](https://github.com/vgambier), [Thomas Karcher](https://github.com/t-karcher), [Janet Cobb](https://github.com/randomnetcat), [yzqzss](https://github.com/yzqzss), [NyaMisty](https://github.com/NyaMisty) and [Rob Kam](https://github.com/robkam)
