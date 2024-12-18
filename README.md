# RxVision

*Transform handwritten prescriptions into digital text with ease.*

RxVision is an OCR-based solution designed to accurately extract and digitize text from handwritten medical prescriptions. Built with a focus on precision and usability, RxVision simplifies the process of reading and interpreting prescription data, helping pharmacists, healthcare professionals, and developers save time and reduce manual errors.

## Key Features
- Accurate recognition of medicine names and prescription details.
- Built-in tools for enhancing text detection, such as image cropping.
- Streamlined processing for handwritten inputs.
- Easy to integrate into pharmacy or healthcare workflows.

## Why RxVision?
RxVision bridges the gap between paper-based prescriptions and digital systems, improving efficiency and ensuring critical medical information is processed seamlessly.

## Ideal For
- Pharmacies looking to digitize prescriptions.
- Healthcare professionals managing patient data.
- Developers building healthcare automation tools.

---

## Usage

RxVision provides two ways to use the application:

1. **Using the Source Code** (for developers and those familiar with Python).
2. **Using the Standalone Executable** (for those who want to run the tool without installing dependencies).

### Option 1: Using the Source Code

#### 1. Clone the Repository
```bash
git clone https://github.com/your-username/RxVision.git
cd RxVision
```

#### 2. Install Dependencies
Ensure you have Python (version 3.8 or higher) installed. Then, install the required packages:
```bash
pip install -r requirements.txt
```

#### 3. Run the Application
- Place your input images in the `input/` folder.
- Run the application:
  ```bash
  python main.py
  ```
- The extracted text will be saved in the `output/` folder.

#### 4. Optional Features
- Use the cropping tool before OCR:
  ```bash
  python crop_tool.py
  ```
- Adjust settings in `config.json` for language, output format, etc.

---

### Option 2: Using the Executable File

#### 1. Download the `.exe` File
- Download the pre-built executable file from the [Releases](https://github.com/your-username/RxVision/releases) section of this repository.

#### 2. Run the Application
- Double-click the `.exe` file to launch the application.
- Follow the on-screen instructions:
  1. Select an input image file or folder.
  2. (Optional) Use the integrated cropping tool for better OCR results.
  3. Extracted text will be saved in the chosen output location.

#### 3. No Installation Required
- The `.exe` file runs standalone and does not require Python or any additional setup.

---

## Example Workflow
1. **Source Code**: Clone the repo, set up dependencies, process images, and save results.
2. **Executable**: Run the `.exe`, select files, and get results instantly.

---

## Contributing
Contributions are welcome! Feel free to open an issue or submit a pull request for improvements or new features.

---

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Support
If you encounter any issues or have questions, please create an issue in this repository or contact us at support@rxvision.com.

