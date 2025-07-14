# Aquila S1000D-AI User Manual
**Version 1.0.0 (July 2025)**


This manual provides step-by-step instructions for using every major feature of the Aquila S1000D-AI prototype. The system consists of a FastAPI backend with either the original React interface or a lightweight HTML/JS page that together help you ingest documents, generate S1000D data modules, and publish technical manuals.

## 1. Installation & Setup
1. Install Python dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
2. (Optional) install the original React frontend:
   ```bash
   cd frontend
   yarn install
   cd ..
   ```
3. Copy `.env.example` in both `backend/` and `frontend/` to `.env` and supply API keys and model names. The system works with OpenAI, Anthropic, or local Hugging Face models.
4. If you change values in `frontend/.env` while `yarn start` is running, restart the command (or use `npm start`) so the updated variables load.
5. Start the services in separate terminals:
   # Alternatively open simple_frontend/index.html for a lightweight interface
   ```bash
   uvicorn backend.websocket_server:app --reload --port 8001
   open simple_frontend/index.html in your browser
   ```
   Open the HTML file directly and it will connect to the WebSocket server on port `8001`.

## 2. Configuring AI Providers
Open the **Provider** modal in the toolbar or call `/api/providers/set` to choose OpenAI, Anthropic, or local models for text and vision tasks. You can also specify model names. The `/api/providers` endpoint returns the current configuration.

## 4. Uploading Documents
Use the **Upload** button to send PDFs or image files to the system. Uploaded files appear in the sidebar. Alternatively, call `/api/documents/upload` with a multipart form. Each document is stored with metadata such as size and checksum.

## 5. Processing Documents
Select a document in the sidebar and click **Process**. The backend extracts text, processes images, and uses the AI providers to generate S1000D data modules and illustration control numbers (ICNs). Processing progress is displayed in the interface.

## 6. Managing Data Modules
Generated data modules are listed under **Data Modules** in the sidebar. Clicking a module opens a viewer in the workspace where you can inspect the verbatim and STE versions. Use the XML editor to modify markup directly. You can also create, update, or delete modules through the `/api/data-modules` endpoints.

### Exporting
A single module can be downloaded as XML through `/api/data-modules/{dmc}/export`.

## 7. Validating Modules
Choose **Validate** in the viewer or call `/api/validate/{dmc}` to run BREX and XSD checks. Validation status is stored with each module and displayed using LED indicators (green, amber, red).

## 8. Fixing Validation Errors
After validating a module you can request automatic fixes. Click **Fix** in the viewer or call `/api/fix-module/{dmc}?method=ai` for an AI-assisted correction. Use `method=manual` to record manual changes. Each action is stored in `audit.log`.

## 9. Illustration Management
Images processed from documents become ICNs. The **Illustrations** tab shows thumbnails with captions, object labels, and hotspot suggestions. You can edit these fields and save changes, which propagate to referencing modules. The raw image is available from `/api/icns/{id}/image`.

## 10. Publication Modules
Create a publication module from the sidebar and arrange data modules in a drag‑and‑drop tree. Metadata such as titles can be edited. Publishing via `/api/publication-modules/{pm_code}/publish` returns a package in the selected formats (XML, HTML, or PDF) and variants (verbatim or STE).

## 11. Testing AI Providers
The **Provider** modal allows quick tests of classification, extraction, captioning, and object detection. These calls correspond to the `/api/test/text` and `/api/test/vision` endpoints.

## 12. Retrieving Default BREX Rules
Download the built-in rule set from `/api/brex-default` to customize validation policies.

## 13. System Health
Check `/api/health` for a status report that includes current provider configuration and timestamp.

## 14. Security Considerations
This simplified setup has no authentication. Avoid exposing it to the public internet.

## 15. Troubleshooting & Testing
Run backend tests with `pytest -q` and frontend tests using `yarn test`. Review `test_result.md` for the testing log. If document processing fails, check the backend console output for errors and verify that provider API keys are correct.
## 16. Audit Log
All create, update and fix actions are recorded in `audit.log` within the upload directory. Review this file for a history of changes to each module.


---
This user manual summarizes how to use every major function of Aquila S1000D-AI, from initial setup through publishing. For architectural details see `README.md`.
