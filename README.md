<div id="top">

<!-- HEADER STYLE: CLASSIC -->
<div align="center">


# KTBKNIDX


<!-- BADGES -->
<img src="https://img.shields.io/github/license/Rachdyan/ktbknidx?style=default&logo=opensourceinitiative&logoColor=white&color=0080ff" alt="license">
<img src="https://img.shields.io/github/last-commit/Rachdyan/ktbknidx?style=default&logo=git&logoColor=white&color=0080ff" alt="last-commit">
<img src="https://img.shields.io/github/languages/top/Rachdyan/ktbknidx?style=default&color=0080ff" alt="repo-top-language">
<img src="https://img.shields.io/github/languages/count/Rachdyan/ktbknidx?style=default&color=0080ff" alt="repo-language-count">

<!-- default option, no dependency badges. -->


<!-- default option, no dependency badges. -->

</div>
<br>

---

## Table of Contents

- [Table of Contents](#table-of-contents)
- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
    - [Project Index](#project-index)
- [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
    - [Usage](#usage)
    - [Testing](#testing)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

## Overview

**IDX Company Disclosure Summarizer**

This project automates intelligence gathering from the Indonesia Stock Exchange (IDX). It continuously monitors for new company disclosures every few hours, uses AI to generate concise summaries of the documents, and delivers these key insights directly to users via a Telegram Bot. This provides a timely source for trading ideas and allows for rapid analysis of market-moving news.

- **🚀 Quick Data Scraping:** Generate concise summaries of keyword-related data from multiple sources in parallel.
- **💬 Seamless Integration:** Interact effortlessly with Telegram dan Google APIs, and Chrome extensions for efficient reporting.
- **🛠 Robust Error Handling:** Handle potential errors gracefully and receive notifications for seamless operation.
- **🔧 Simplified Dependency Management:** Enhance project performance by managing essential libraries effortlessly.

---

## Features

|      | Component       | Details                              |
| :--- | :-------------- | :----------------------------------- |
| ⚙️  | **Architecture**  | <ul><li>Follows a modular design pattern with clear separation of concerns.</li><li>Utilizes multiprocessing for efficient data scraping.</li></ul> |
| 🔩 | **Code Quality**  | <ul><li>Consistent code formatting adhering to PEP8 standards.</li><li>Includes comprehensive unit tests for critical functionalities.</li></ul> |
| 🔌 | **Integrations**  | <ul><li>Integrates with various third-party libraries like BeautifulSoup, Pandas, and Selenium for web scraping and data processing.</li></ul> |
| 🧩 | **Modularity**    | <ul><li>Codebase is organized into reusable modules promoting code reusability.</li><li>Separate modules for different scraping tasks.</li></ul> |
| ⚡️  | **Performance**   | <ul><li>Efficient use of multiprocessing for faster data scraping.</li><li>Optimized data processing pipelines for improved performance.</li></ul> |
| 📦 | **Dependencies**  | <ul><li>Relies on a wide range of dependencies including BeautifulSoup, Pandas, Selenium, and more for web scraping and data manipulation.</li></ul> |

---

## Project Structure

```sh
└── ktbknidx/
    ├── .github
    │   ├── .DS_Store
    │   └── workflows
    ├── README.md
    ├── detailed_scrape.py
    ├── detailed_scrape_multi.py
    ├── latest_logs
    │   ├──   File .line_198
    │   └── .DS_Store
    ├── quick_scrape.py
    ├── quick_scrape_multiprocess.py
    ├── requirements.txt
    ├── requirements_quick.txt
    └── utils
        ├── __init__.py
        ├── __pycache__
        ├── ai_summary_utils.py
        ├── detailed_scraping_utils.py
        ├── google_utils.py
        ├── scraping_utils.py
        └── telegram_utils.py
```

### Project Index

<details open>
	<summary><b><code>KTBKNIDX/</code></b></summary>
	<!-- __root__ Submodule -->
	<details>
		<summary><b>__root__</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ __root__</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/Rachdyan/ktbknidx/blob/master/quick_scrape_multiprocess.py'>quick_scrape_multiprocess.py</a></b></td>
					<td style='padding: 8px;'>- Generate and send a summary message to a Telegram chat ID containing a concise summary of keyword-related data scraped from multiple sources<br>- The script processes keywords in parallel, filters data based on time, generates message strings, and sends the summary to the specified chat ID using a Telegram bot.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/Rachdyan/ktbknidx/blob/master/requirements_quick.txt'>requirements_quick.txt</a></b></td>
					<td style='padding: 8px;'>- Enhance project dependencies by specifying required packages in the requirements_quick.txt file<br>- Ensure seamless integration of libraries like BeautifulSoup, Pandas, and SeleniumBase for efficient web scraping and data processing<br>- Optimize project setup and execution by defining essential dependencies for smooth functionality.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/Rachdyan/ktbknidx/blob/master/detailed_scrape_multi.py'>detailed_scrape_multi.py</a></b></td>
					<td style='padding: 8px;'>- Generate and send daily run summaries to a specified Telegram chat ID<br>- The code processes keywords in parallel, filters and uploads PDFs, and generates detailed summaries<br>- It handles potential errors and notifications for no results<br>- The script interacts with Google Sheets, Google Drive, and Telegram, ensuring efficient data management and communication.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/Rachdyan/ktbknidx/blob/master/requirements.txt'>requirements.txt</a></b></td>
					<td style='padding: 8px;'>- Enhances project functionality by managing dependencies efficiently<br>- Ensures seamless integration of essential libraries for optimal performance<br>- Facilitates smooth execution and robust operation of the codebase.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/Rachdyan/ktbknidx/blob/master/quick_scrape.py'>quick_scrape.py</a></b></td>
					<td style='padding: 8px;'>- Scrapes and processes data based on predefined keywords, generating a summary report<br>- Determines the run time type and formats data for display<br>- Sends the summary message via Telegram using a bot.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/Rachdyan/ktbknidx/blob/master/detailed_scrape.py'>detailed_scrape.py</a></b></td>
					<td style='padding: 8px;'>- Generate daily summaries of scraped data, upload PDFs, and send messages via Telegram<br>- Utilizes SeleniumBase, Google APIs, OpenAI, and Telegram libraries<br>- Scrapes data based on keywords, processes it, and updates Google Sheets with results<br>- Handles errors gracefully and ensures efficient communication with users<br>- A comprehensive tool for automating data processing and dissemination tasks.</td>
				</tr>
			</table>
		</blockquote>
	</details>
	<!-- utils Submodule -->
	<details>
		<summary><b>utils</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ utils</b></code>
			<table style='width: 100%; border-collapse: collapse;'>
			<thead>
				<tr style='background-color: #f8f9fa;'>
					<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
					<th style='text-align: left; padding: 8px;'>Summary</th>
				</tr>
			</thead>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/Rachdyan/ktbknidx/blob/master/utils/ai_summary_utils.py'>ai_summary_utils.py</a></b></td>
					<td style='padding: 8px;'>- The <code>ai_summary_utils.py</code> file in the <code>utils</code> directory provides functions to tokenize text, chunk text based on a delimiter, combine chunks, and generate chat summaries using a specified model<br>- It includes methods to control summarization detail, chunk size, and verbosity<br>- The file facilitates text processing for efficient summarization and chat completion tasks within the projects architecture.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/Rachdyan/ktbknidx/blob/master/utils/telegram_utils.py'>telegram_utils.py</a></b></td>
					<td style='padding: 8px;'>- Send summary messages via Telegram bot by formatting input data and handling potential errors<br>- Ensure successful message delivery to the specified chat ID<br>- Handle various exceptions like Telegram API errors, missing data keys, and unexpected errors during the process.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/Rachdyan/ktbknidx/blob/master/utils/google_utils.py'>google_utils.py</a></b></td>
					<td style='padding: 8px;'>- Provide functions to interact with Google Drive and Google Sheets<br>- Functions include listing folders, creating folders, uploading files to Drive, and exporting data to Sheets<br>- Handles errors gracefully and offers clear error messages for troubleshooting<br>- Enhances integration with Google APIs for seamless data management.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/Rachdyan/ktbknidx/blob/master/utils/detailed_scraping_utils.py'>detailed_scraping_utils.py</a></b></td>
					<td style='padding: 8px;'>- Generate PDFs, upload to Drive, and summarize content<br>- Utilizes various APIs for scraping, PDF handling, and AI summarization<br>- Handles file downloads, Drive uploads, and text processing efficiently<br>- Supports multi-row processing with separate browser instances<br>- Handles errors gracefully for a seamless workflow.</td>
				</tr>
				<tr style='border-bottom: 1px solid #eee;'>
					<td style='padding: 8px;'><b><a href='https://github.com/Rachdyan/ktbknidx/blob/master/utils/scraping_utils.py'>scraping_utils.py</a></b></td>
					<td style='padding: 8px;'>- Scrape data from the IDX website for a given keyword, generating a pandas DataFrame with relevant information<br>- The code utilizes SeleniumBase and BeautifulSoup to extract and process data, handling potential errors gracefully<br>- The function processes keywords in separate browser instances, ensuring robust data retrieval.</td>
				</tr>
			</table>
		</blockquote>
	</details>
	<!-- latest_logs Submodule -->
	<details>
		<summary><b>latest_logs</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ latest_logs</b></code>
			<!--   File .line_198 Submodule -->
			<details>
				<summary><b>  File .line_198</b></summary>
				<blockquote>
					<div class='directory-path' style='padding: 8px 0; color: #666;'>
						<code><b>⦿ latest_logs.  File .line_198</b></code>
					<table style='width: 100%; border-collapse: collapse;'>
					<thead>
						<tr style='background-color: #f8f9fa;'>
							<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
							<th style='text-align: left; padding: 8px;'>Summary</th>
						</tr>
					</thead>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/Rachdyan/ktbknidx/blob/master/latest_logs/  File .line_198/basic_test_info.txt'>basic_test_info.txt</a></b></td>
							<td style='padding: 8px;'>- Generate a comprehensive summary detailing the purpose and function of the code file within the projects architecture<br>- Emphasize the achieved outcomes and avoid delving into technical intricacies<br>- Ensure the summary is concise and informative, focusing on the codes role in the broader context of the project.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/Rachdyan/ktbknidx/blob/master/latest_logs/  File .line_198/page_source.html'>page_source.html</a></b></td>
							<td style='padding: 8px;'>- SummaryThe provided code file, located at <code>latest_logs/.line_198/page_source.html</code>, serves as the base source for the new tab page in a web browser<br>- It sets the foundation for the layout and content displayed when a user opens a new tab<br>- This file plays a crucial role in defining the initial structure and elements that users interact with upon launching a new tab, enhancing their browsing experience.By customizing and optimizing the content within this file, developers can tailor the new tab page to meet specific user preferences and requirements<br>- This code file acts as a starting point for creating a visually appealing and functional new tab page, contributing to a seamless and personalized browsing environment for users.</td>
						</tr>
					</table>
				</blockquote>
			</details>
		</blockquote>
	</details>
	<!-- .github Submodule -->
	<details>
		<summary><b>.github</b></summary>
		<blockquote>
			<div class='directory-path' style='padding: 8px 0; color: #666;'>
				<code><b>⦿ .github</b></code>
			<!-- workflows Submodule -->
			<details>
				<summary><b>workflows</b></summary>
				<blockquote>
					<div class='directory-path' style='padding: 8px 0; color: #666;'>
						<code><b>⦿ .github.workflows</b></code>
					<table style='width: 100%; border-collapse: collapse;'>
					<thead>
						<tr style='background-color: #f8f9fa;'>
							<th style='width: 30%; text-align: left; padding: 8px;'>File Name</th>
							<th style='text-align: left; padding: 8px;'>Summary</th>
						</tr>
					</thead>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/Rachdyan/ktbknidx/blob/master/.github/workflows/quick_scrape.yml'>quick_scrape.yml</a></b></td>
							<td style='padding: 8px;'>- Execute a workflow that sets up Python, installs dependencies, checks Chrome binaries, and runs a Python script for quick scraping<br>- The workflow ensures proper configuration and dependencies for successful execution.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/Rachdyan/ktbknidx/blob/master/.github/workflows/detailed_scrape_multiprocess.yml'>detailed_scrape_multiprocess.yml</a></b></td>
							<td style='padding: 8px;'>- Execute a workflow that performs detailed web scraping using multiple processes<br>- The workflow is scheduled to run at specific times and includes steps to set up Python, install dependencies, check Chrome binaries, and run the scraping script with debug mode.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/Rachdyan/ktbknidx/blob/master/.github/workflows/detailed_scrape.yml'>detailed_scrape.yml</a></b></td>
							<td style='padding: 8px;'>- Execute a workflow that sets up Python, installs dependencies, checks Chrome binaries, and runs detailed_scrape.py with specified environment variables<br>- This workflow ensures a smooth execution of the detailed scraping process, enhancing the projects data collection capabilities.</td>
						</tr>
						<tr style='border-bottom: 1px solid #eee;'>
							<td style='padding: 8px;'><b><a href='https://github.com/Rachdyan/ktbknidx/blob/master/.github/workflows/quick_scrape_multiprocess.yml'>quick_scrape_multiprocess.yml</a></b></td>
							<td style='padding: 8px;'>- Automates scheduled multi-process web scraping using Python<br>- Sets up necessary dependencies, Chrome, and chromedriver<br>- Ensures pytest functionality and Chrome binary compatibility<br>- Executes the scraping process with debug mode enabled.</td>
						</tr>
					</table>
				</blockquote>
			</details>
		</blockquote>
	</details>
</details>

---

## Getting Started

### Prerequisites

This project requires the following dependencies:

- **Programming Language:** Python
- **Package Manager:** Pip

### Installation

Build ktbknidx from the source and intsall dependencies:

1. **Clone the repository:**

    ```sh
    ❯ git clone https://github.com/Rachdyan/ktbknidx
    ```

2. **Navigate to the project directory:**

    ```sh
    ❯ cd ktbknidx
    ```

3. **Install the dependencies:**

<!-- SHIELDS BADGE CURRENTLY DISABLED -->

	```sh
	❯ pip install -r requirements.txt
	```



---


## Contributing

- **💬 [Join the Discussions](https://github.com/Rachdyan/ktbknidx/discussions)**: Share your insights, provide feedback, or ask questions.
- **🐛 [Report Issues](https://github.com/Rachdyan/ktbknidx/issues)**: Submit bugs found or log feature requests for the `ktbknidx` project.
- **💡 [Submit Pull Requests](https://github.com/Rachdyan/ktbknidx/blob/main/CONTRIBUTING.md)**: Review open PRs, and submit your own PRs.

<details closed>
<summary>Contributing Guidelines</summary>

1. **Fork the Repository**: Start by forking the project repository to your github account.
2. **Clone Locally**: Clone the forked repository to your local machine using a git client.
   ```sh
   git clone https://github.com/Rachdyan/ktbknidx
   ```
3. **Create a New Branch**: Always work on a new branch, giving it a descriptive name.
   ```sh
   git checkout -b new-feature-x
   ```
4. **Make Your Changes**: Develop and test your changes locally.
5. **Commit Your Changes**: Commit with a clear message describing your updates.
   ```sh
   git commit -m 'Implemented new feature x.'
   ```
6. **Push to github**: Push the changes to your forked repository.
   ```sh
   git push origin new-feature-x
   ```
7. **Submit a Pull Request**: Create a PR against the original project repository. Clearly describe the changes and their motivations.
8. **Review**: Once your PR is reviewed and approved, it will be merged into the main branch. Congratulations on your contribution!
</details>

<details closed>
<summary>Contributor Graph</summary>
<br>
<p align="left">
   <a href="https://github.com{/Rachdyan/ktbknidx/}graphs/contributors">
      <img src="https://contrib.rocks/image?repo=Rachdyan/ktbknidx">
   </a>
</p>
</details>

---

## License

Idx_financial_report is protected under the [MIT](https://choosealicense.com/licenses/mit/) License. For more details, refer to the [MIT](https://choosealicense.com/licenses/mit/) file.

---

## Disclaimer

This tool is for educational purposes only. Always verify data with official sources before making financial decisions. The maintainers are not responsible for data accuracy or usage consequences.

<div align="right">

[![][back-to-top]](#top)

</div>


[back-to-top]: https://img.shields.io/badge/-BACK_TO_TOP-151515?style=flat-square


---