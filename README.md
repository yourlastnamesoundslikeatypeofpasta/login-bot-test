# login-bot-test
<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
    <li><a href="#python-requirements">Python Requirements</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#latest-changes">Latest Changes</a></li>
    <li><a href="#known-issues">Known Issues</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#acknowledgements">Acknowledgements</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## About The Project
An **alpha, proof of concept**, Slack Bot. This alpha version uses Python's built in 
[HTTPServer](https://docs.python.org/3/library/http.server.html) for local development. When a majority of this
proof of concept is complete, a production version will be written using a proper framework, either Flask, or Django.

### Built With
* Python 3.9.7
* [Slack Bolt for Python](https://api.slack.com/tools/bolt)

<!-- GETTING STARTED -->
## Getting Started
### Prerequisites
### Python Requirements
* [requirements.txt](https://github.com/yourlastnamesoundslikeatypeofpasta/login-bot-test/blob/main/requirements.txt)
### Installation

<!-- USAGE EXAMPLES -->
## Usage

<!-- ROADMAP -->
## Roadmap

<!-- LATEST CHANGES -->
## Recent Changes
###09/03/21
* Reworked Piece Pay calculator. It's now 100% functional.
###09/02/21
* Users within private triage groups can now claim a dispute. After a dispute is claimed, "approve" and "deny" buttons will appear. 
<!-- KNOWN ISSUES -->
## Known Issues
###09/03/21
* Broken Links. Links pertaining to a package with a letter prefixed suite (ex: N1234, L1234) will not open in backoffice. This is due to backoffice translating these suits into a 6 digit suite on the backend.
* Text cutoff on iOS. If a message is formatted with [code blocks](https://api.slack.com/reference/surfaces/formatting#block-formatting) and sent by the Slack bot, the text has a tendency to get cut off on the iOS client, but is fine on Desktop Clients. I contacted Slack, and they said this is a currently known bug. Messages will be reformatted soon.

<!-- LICENSE -->
## License

<!-- CONTACT -->
## Contact

<!-- ACKNOWLEDGEMENTS -->
## Acknowledgements



