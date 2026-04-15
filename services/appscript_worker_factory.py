"""
Q.G.T.N.L. (0) // APPS SCRIPT WORKER FACTORY
Templates and generation for Google Apps Script workers.
Produces ready-to-deploy .gs files for Google Workspace automation.
"""
import json
from datetime import datetime, timezone

# Pre-built worker templates
WORKER_TEMPLATES = {
    "sheet_processor": {
        "name": "Sheet Data Processor",
        "description": "Processes Google Sheets data with custom logic",
        "triggers": ["onOpen", "onEdit"],
        "template": '''/**
 * Citadel Worker: Sheet Data Processor
 * Generated: {timestamp}
 * Authority: Q.G.T.N.L. Citadel Omega
 */

// ── Configuration ──
const CONFIG = {{
  SHEET_NAME: "Sheet1",
  LOG_SHEET: "Logs",
  ADMIN_EMAIL: "",  // Set your email
}};

/**
 * Runs when the spreadsheet is opened.
 */
function onOpen() {{
  const ui = SpreadsheetApp.getUi();
  ui.createMenu("🏛️ Citadel")
    .addItem("Process Data", "processAllData")
    .addItem("Generate Report", "generateReport")
    .addSeparator()
    .addItem("View Logs", "showLogs")
    .addToUi();
}}

/**
 * Processes all data in the configured sheet.
 */
function processAllData() {{
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(CONFIG.SHEET_NAME);
  if (!sheet) {{
    SpreadsheetApp.getUi().alert("Sheet not found: " + CONFIG.SHEET_NAME);
    return;
  }}
  const data = sheet.getDataRange().getValues();
  const headers = data[0];
  let processed = 0;

  for (let i = 1; i < data.length; i++) {{
    try {{
      // Custom processing logic here
      processed++;
    }} catch (e) {{
      logError("Row " + (i + 1) + ": " + e.message);
    }}
  }}

  logInfo("Processed " + processed + " rows");
  SpreadsheetApp.getUi().alert("✅ Processed " + processed + " rows");
}}

/**
 * Generates a summary report.
 */
function generateReport() {{
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(CONFIG.SHEET_NAME);
  const data = sheet.getDataRange().getValues();

  let reportSheet = ss.getSheetByName("Report");
  if (!reportSheet) {{
    reportSheet = ss.insertSheet("Report");
  }}
  reportSheet.clear();
  reportSheet.appendRow(["Report Generated", new Date()]);
  reportSheet.appendRow(["Total Rows", data.length - 1]);

  logInfo("Report generated");
}}

// ── Logging ──
function logInfo(msg) {{
  _log("INFO", msg);
}}

function logError(msg) {{
  _log("ERROR", msg);
}}

function _log(level, msg) {{
  try {{
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    let logSheet = ss.getSheetByName(CONFIG.LOG_SHEET);
    if (!logSheet) {{
      logSheet = ss.insertSheet(CONFIG.LOG_SHEET);
      logSheet.appendRow(["Timestamp", "Level", "Message"]);
    }}
    logSheet.appendRow([new Date(), level, msg]);
  }} catch (e) {{
    console.log(level + ": " + msg);
  }}
}}

function showLogs() {{
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const logSheet = ss.getSheetByName(CONFIG.LOG_SHEET);
  if (logSheet) {{
    ss.setActiveSheet(logSheet);
  }} else {{
    SpreadsheetApp.getUi().alert("No logs found.");
  }}
}}
''',
    },
    "email_automation": {
        "name": "Email Automation Worker",
        "description": "Automates email sending and processing via Gmail",
        "triggers": ["time-based"],
        "template": '''/**
 * Citadel Worker: Email Automation
 * Generated: {timestamp}
 * Authority: Q.G.T.N.L. Citadel Omega
 */

// ── Configuration ──
const CONFIG = {{
  CHECK_INTERVAL_MINUTES: 15,
  LABEL_PROCESSED: "Processed",
  LABEL_PENDING: "Pending",
  MAX_EMAILS_PER_RUN: 50,
}};

/**
 * Time-based trigger: process pending emails.
 * Set up via: setupTrigger()
 */
function processEmails() {{
  const threads = GmailApp.search("label:" + CONFIG.LABEL_PENDING, 0, CONFIG.MAX_EMAILS_PER_RUN);
  let processed = 0;

  threads.forEach(function(thread) {{
    try {{
      const messages = thread.getMessages();
      messages.forEach(function(msg) {{
        // Custom email processing logic
        const subject = msg.getSubject();
        const body = msg.getPlainBody();
        const from = msg.getFrom();

        console.log("Processing: " + subject + " from " + from);
        // Add your processing logic here
      }});

      // Mark as processed
      const label = GmailApp.getUserLabelByName(CONFIG.LABEL_PROCESSED)
                    || GmailApp.createLabel(CONFIG.LABEL_PROCESSED);
      thread.addLabel(label);

      const pendingLabel = GmailApp.getUserLabelByName(CONFIG.LABEL_PENDING);
      if (pendingLabel) thread.removeLabel(pendingLabel);

      processed++;
    }} catch (e) {{
      console.error("Error processing thread: " + e.message);
    }}
  }});

  console.log("Processed " + processed + " email threads");
}}

/**
 * Sets up the time-based trigger.
 */
function setupTrigger() {{
  // Remove existing triggers for this function
  ScriptApp.getProjectTriggers().forEach(function(trigger) {{
    if (trigger.getHandlerFunction() === "processEmails") {{
      ScriptApp.deleteTrigger(trigger);
    }}
  }});

  ScriptApp.newTrigger("processEmails")
    .timeBased()
    .everyMinutes(CONFIG.CHECK_INTERVAL_MINUTES)
    .create();

  console.log("Trigger created: every " + CONFIG.CHECK_INTERVAL_MINUTES + " minutes");
}}

/**
 * Send a templated email.
 */
function sendTemplatedEmail(to, subject, templateData) {{
  const template = HtmlService.createTemplateFromFile("email_template");
  Object.keys(templateData).forEach(function(key) {{
    template[key] = templateData[key];
  }});
  const htmlBody = template.evaluate().getContent();

  GmailApp.sendEmail(to, subject, "", {{
    htmlBody: htmlBody,
    name: "Citadel Automation",
  }});
}}
''',
    },
    "drive_organizer": {
        "name": "Drive File Organizer",
        "description": "Organizes and catalogues Google Drive files",
        "triggers": ["time-based", "onOpen"],
        "template": '''/**
 * Citadel Worker: Drive File Organizer
 * Generated: {timestamp}
 * Authority: Q.G.T.N.L. Citadel Omega
 */

// ── Configuration ──
const CONFIG = {{
  ROOT_FOLDER_ID: "",     // Set the root folder ID to organize
  LOG_SPREADSHEET_ID: "", // Set spreadsheet ID for logging
  MAX_FILES_PER_RUN: 100,
}};

/**
 * Scans and catalogues all files in the root folder.
 */
function catalogueFiles() {{
  const rootFolder = CONFIG.ROOT_FOLDER_ID
    ? DriveApp.getFolderById(CONFIG.ROOT_FOLDER_ID)
    : DriveApp.getRootFolder();

  const results = [];
  _scanFolder(rootFolder, "", results, 0);

  // Write results to a spreadsheet
  if (CONFIG.LOG_SPREADSHEET_ID) {{
    const ss = SpreadsheetApp.openById(CONFIG.LOG_SPREADSHEET_ID);
    let sheet = ss.getSheetByName("Catalogue");
    if (!sheet) sheet = ss.insertSheet("Catalogue");
    sheet.clear();
    sheet.appendRow(["Name", "Type", "Size (KB)", "Path", "Last Updated", "URL"]);
    results.forEach(function(r) {{
      sheet.appendRow([r.name, r.type, r.sizeKB, r.path, r.lastUpdated, r.url]);
    }});
  }}

  console.log("Catalogued " + results.length + " files");
  return results;
}}

function _scanFolder(folder, path, results, depth) {{
  if (depth > 10 || results.length >= CONFIG.MAX_FILES_PER_RUN) return;

  const currentPath = path + "/" + folder.getName();

  // Process files
  const files = folder.getFiles();
  while (files.hasNext() && results.length < CONFIG.MAX_FILES_PER_RUN) {{
    const file = files.next();
    results.push({{
      name: file.getName(),
      type: file.getMimeType(),
      sizeKB: Math.round(file.getSize() / 1024),
      path: currentPath,
      lastUpdated: file.getLastUpdated(),
      url: file.getUrl(),
    }});
  }}

  // Recurse into subfolders
  const subfolders = folder.getFolders();
  while (subfolders.hasNext()) {{
    _scanFolder(subfolders.next(), currentPath, results, depth + 1);
  }}
}}

/**
 * Organize files by type into subfolders.
 */
function organizeByType() {{
  const rootFolder = CONFIG.ROOT_FOLDER_ID
    ? DriveApp.getFolderById(CONFIG.ROOT_FOLDER_ID)
    : DriveApp.getRootFolder();

  const typeMap = {{
    "application/pdf": "PDFs",
    "image/": "Images",
    "video/": "Videos",
    "audio/": "Audio",
    "application/vnd.google-apps.spreadsheet": "Sheets",
    "application/vnd.google-apps.document": "Docs",
  }};

  const files = rootFolder.getFiles();
  let moved = 0;

  while (files.hasNext()) {{
    const file = files.next();
    const mimeType = file.getMimeType();

    for (const [pattern, folderName] of Object.entries(typeMap)) {{
      if (mimeType.startsWith(pattern)) {{
        let targetFolder;
        const folders = rootFolder.getFoldersByName(folderName);
        targetFolder = folders.hasNext()
          ? folders.next()
          : rootFolder.createFolder(folderName);

        file.moveTo(targetFolder);
        moved++;
        break;
      }}
    }}
  }}

  console.log("Organized " + moved + " files");
}}

/**
 * Set up the automatic trigger.
 */
function setupTrigger() {{
  ScriptApp.getProjectTriggers().forEach(function(trigger) {{
    if (trigger.getHandlerFunction() === "catalogueFiles") {{
      ScriptApp.deleteTrigger(trigger);
    }}
  }});

  ScriptApp.newTrigger("catalogueFiles")
    .timeBased()
    .everyHours(6)
    .create();
}}
''',
    },
    "webhook_receiver": {
        "name": "Webhook Receiver",
        "description": "Receives webhooks via doPost and processes payloads",
        "triggers": ["web app"],
        "template": '''/**
 * Citadel Worker: Webhook Receiver
 * Generated: {timestamp}
 * Authority: Q.G.T.N.L. Citadel Omega
 * Deploy as Web App: Execute as Me, Anyone can access
 */

// ── Configuration ──
const CONFIG = {{
  LOG_SHEET_ID: "",    // Set spreadsheet ID for logging
  SECRET_TOKEN: "",    // Optional: webhook secret for verification
}};

/**
 * Handles GET requests (health check).
 */
function doGet(e) {{
  return ContentService.createTextOutput(
    JSON.stringify({{
      status: "online",
      service: "Citadel Webhook Receiver",
      timestamp: new Date().toISOString(),
    }})
  ).setMimeType(ContentService.MimeType.JSON);
}}

/**
 * Handles POST requests (webhook payloads).
 */
function doPost(e) {{
  try {{
    const payload = JSON.parse(e.postData.contents);

    // Optional token verification
    if (CONFIG.SECRET_TOKEN && payload.token !== CONFIG.SECRET_TOKEN) {{
      return _jsonResponse({{ error: "Unauthorized" }}, 401);
    }}

    // Log the incoming webhook
    _logWebhook(payload);

    // Route to handler based on event type
    const eventType = payload.event || payload.type || "unknown";
    const result = _handleEvent(eventType, payload);

    return _jsonResponse({{ success: true, event: eventType, result: result }});
  }} catch (error) {{
    console.error("Webhook error: " + error.message);
    return _jsonResponse({{ error: error.message }}, 500);
  }}
}}

function _handleEvent(eventType, payload) {{
  switch (eventType) {{
    case "push":
      return _handlePush(payload);
    case "sync":
      return _handleSync(payload);
    default:
      console.log("Unhandled event: " + eventType);
      return {{ handled: false, event: eventType }};
  }}
}}

function _handlePush(payload) {{
  console.log("Push event received: " + JSON.stringify(payload).substring(0, 200));
  return {{ handled: true }};
}}

function _handleSync(payload) {{
  console.log("Sync event received");
  return {{ handled: true }};
}}

function _logWebhook(payload) {{
  if (!CONFIG.LOG_SHEET_ID) return;
  try {{
    const ss = SpreadsheetApp.openById(CONFIG.LOG_SHEET_ID);
    let sheet = ss.getSheetByName("Webhooks");
    if (!sheet) {{
      sheet = ss.insertSheet("Webhooks");
      sheet.appendRow(["Timestamp", "Event", "Payload"]);
    }}
    const event = payload.event || payload.type || "unknown";
    sheet.appendRow([new Date(), event, JSON.stringify(payload).substring(0, 1000)]);
  }} catch (e) {{
    console.error("Logging error: " + e.message);
  }}
}}

function _jsonResponse(data, code) {{
  return ContentService.createTextOutput(JSON.stringify(data))
    .setMimeType(ContentService.MimeType.JSON);
}}
''',
    },
}

# Default manifest for Apps Script projects
DEFAULT_MANIFEST = {
    "timeZone": "Australia/Sydney",
    "dependencies": {},
    "exceptionLogging": "STACKDRIVER",
    "runtimeVersion": "V8",
    "webapp": {"executeAs": "USER_DEPLOYING", "access": "ANYONE"},
}


def get_template_names() -> list[str]:
    """Return available template names."""
    return list(WORKER_TEMPLATES.keys())


def get_template(name: str) -> dict | None:
    """Get a worker template by name."""
    return WORKER_TEMPLATES.get(name)


def render_template(name: str) -> str | None:
    """Render a worker template with current timestamp."""
    template = WORKER_TEMPLATES.get(name)
    if not template:
        return None
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    return template["template"].format(timestamp=timestamp)


def get_manifest(scopes: list | None = None) -> str:
    """Generate an appsscript.json manifest."""
    manifest = dict(DEFAULT_MANIFEST)
    if scopes:
        manifest["oauthScopes"] = scopes
    return json.dumps(manifest, indent=2)
