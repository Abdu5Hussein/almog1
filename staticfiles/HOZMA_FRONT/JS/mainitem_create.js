  // Extract the source/client ID from the URL and inject it into the form field
  document.addEventListener("DOMContentLoaded", function () {
    const pathParts = window.location.pathname.split("/").filter(Boolean);
    const lastPart = pathParts[pathParts.length - 1];
    
    // Check if it's a number
    const sourceId = parseInt(lastPart);
    if (!isNaN(sourceId)) {
      const sourceInput = document.getElementById("source");
      if (sourceInput) {
        sourceInput.value = sourceId;
      }
    }
    
    // Set up file upload functionality
    setupFileUpload();
    
    // Set up template download
    document.getElementById('download-template').addEventListener('click', function(e) {
      e.preventDefault();
      downloadTemplate();
    });
  });

  // Single item form submission
  function addJsonField(key = '', value = '') {
  const container = document.getElementById('json-fields');
  const div = document.createElement('div');
  div.className = 'd-flex mb-2';

  div.innerHTML = `
    <input type="text" class="form-control me-2" placeholder="المفتاح" value="${key}" oninput="updateJsonHiddenInput()" />
    <input type="text" class="form-control me-2" placeholder="القيمة" value="${value}" oninput="updateJsonHiddenInput()" />
    <button type="button" class="btn btn-danger btn-sm" onclick="this.parentElement.remove(); updateJsonHiddenInput()">-</button>
  `;

  container.appendChild(div);
  updateJsonHiddenInput();
}

function updateJsonHiddenInput() {
  const container = document.getElementById('json-fields');
  const inputs = container.querySelectorAll('input');
  const json = {};

  for (let i = 0; i < inputs.length; i += 2) {
    const key = inputs[i].value.trim();
    const value = inputs[i + 1].value.trim();
    if (key) json[key] = value;
  }

  document.getElementById('json_description').value = JSON.stringify(json);
}

document.getElementById("mainitem-form").addEventListener("submit", async function(event) {
  event.preventDefault();
  const form = event.target;
  updateJsonHiddenInput(); // Make sure the hidden input is updated before reading it

  const formData = new FormData(form);
  const data = {};

  for (let [key, value] of formData.entries()) {
    data[key] = value || null;
  }

  // Handle JSON description
  if (data.json_description) {
    try {
      data.json_description = JSON.parse(data.json_description);
    } catch {
      showResponse("JSON غير صالح", "error");
      return;
    }
  }



  try {
    console.log("Request Body:", JSON.stringify(data));
    const response = await customFetch("http://45.13.59.226/hozma/api/mainitem/create/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
      
    });

    const result = await response.json();
   

    if (response.ok) {
      showResponse(result.message || "تم إنشاء العنصر بنجاح", "success");
      form.reset();
      document.getElementById('json-fields').innerHTML = ""; // Clear JSON fields
    } else {
      showResponse(result.message || "حدث خطأ أثناء إنشاء العنصر", "error");
    }
  } catch (error) {
    showResponse("حدث خطأ في الاتصال بالخادم", "error");
    console.error("Error:", error);
  }
});
  
  // File upload functionality
  function setupFileUpload() {
const dropArea = document.getElementById('drop-area');
const fileInput = document.getElementById('file-input');
const fileInfo = document.getElementById('file-info');
const fileName = document.getElementById('file-name');
const removeFile = document.getElementById('remove-file');
const uploadBtn = document.getElementById('upload-btn');
const progressBar = document.getElementById('progress-bar');

let selectedFile = null;



dropArea.addEventListener('click', () => {
 
  fileInput.click();
});

fileInput.addEventListener('change', function(e) {
  if (e.target.files.length) {
  
    handleFileSelection(e.target.files[0]);
  }
});

['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
  dropArea.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
  e.preventDefault();
  e.stopPropagation();
}

['dragenter', 'dragover'].forEach(eventName => {
  dropArea.addEventListener(eventName, highlight, false);
});

['dragleave', 'drop'].forEach(eventName => {
  dropArea.addEventListener(eventName, unhighlight, false);
});

function highlight() {
  dropArea.style.borderColor = '#3498db';
  dropArea.style.backgroundColor = 'rgba(52, 152, 219, 0.1)';
}

function unhighlight() {
  dropArea.style.borderColor = '#ced4da';
  dropArea.style.backgroundColor = '#f8f9fa';
}

dropArea.addEventListener('drop', function(e) {
  const dt = e.dataTransfer;
  const file = dt.files[0];
 
  handleFileSelection(file);
});

removeFile.addEventListener('click', function(e) {
  e.preventDefault();
  e.stopPropagation();
 
  selectedFile = null;
  fileInput.value = '';
  fileInfo.style.display = 'none';
  uploadBtn.disabled = true;
});

uploadBtn.addEventListener('click', function() {
  if (selectedFile) {
   
    uploadFile(selectedFile);
  }
});

function handleFileSelection(file) {
 
  const validTypes = [
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.ms-excel'
  ];

  if (!validTypes.includes(file.type) && !file.name.match(/\.(xlsx|xls)$/)) {
    console.warn("[ERROR] Invalid file type selected.");
    showResponse('الرجاء اختيار ملف إكسل صالح', 'error');
    return;
  }

  selectedFile = file;
  fileName.textContent = file.name;
  fileInfo.style.display = 'block';
  uploadBtn.disabled = false;
  
}
// ⬇️  النسخة الكاملة المحدَّثة من الدالة uploadFile
async function uploadFile(file) {
try {
  // إظهار شريط التقدم
  progressBar.style.display = 'block';
  const progressBarInner = progressBar.querySelector('.progress-bar');

  /* 1) قراءة ملف إكسل */
  const { rawRows, mappedRows, headers } = await readExcelFile(file, progressBarInner);
  if (!mappedRows || mappedRows.length === 0) {
    console.warn('[ERROR] No valid data in Excel file.');
    showResponse('الملف لا يحتوي على بيانات صالحة', 'error');
    return;
  }

  /* 2) استخراج sourceId من رابط الصفحة */
  const pathParts = window.location.pathname.split('/').filter(Boolean);
  const sourceId  = pathParts[pathParts.length - 1];
  if (!sourceId) {
    showResponse('لا يمكن تحديد معرف المصدر', 'error');
    return;
  }

  /* 3) تجهيز البيانات قبل الإرسال */
  mappedRows.forEach(item => {
    item.source = sourceId;
    if (item.json_description && typeof item.json_description === 'string') {
      try {
        item.json_description = JSON.parse(item.json_description);
      } catch (e) {
        console.warn('[WARN] JSON parsing failed for description:', e);
        item.json_description = null;
      }
    }
  });

  const results = [];

  /* 4) رفع كل صفّ */
  for (let i = 0; i < mappedRows.length; i++) {
    const item        = mappedRows[i];
    const originalRow = rawRows[i];  // مهما كان يحتوي، حتى القيم الفارغة

    const progress = Math.min(100, Math.round((i / mappedRows.length) * 100));
    progressBarInner.style.width  = `${progress}%`;
    progressBarInner.textContent = `${progress}%`;

    console.log(`[DEBUG] Sending item ${i + 1}/${mappedRows.length}:`, JSON.stringify(item, null, 2));

    try {
      const response = await customFetch('http://45.13.59.226/hozma/api/mainitem/create/', {
        method  : 'POST',
        headers : { 'Content-Type': 'application/json' },
        body    : JSON.stringify(item),
      });

      const result = await response.json();
      console.log(`[DEBUG] Response for item ${i + 1}/${mappedRows.length} (PNO: ${item.pno || 'N/A'}):`, result);

      if (!item.pno && result?.data?.pno) {
        item.pno = result.data.pno;
      }

      if (response.ok && result.success !== false) {
        results.push({
          ...item,
          success     : true,
          message     : result.message || 'تمت الإضافة بنجاح',
          originalRow,
        });
      } else {
        const errorMessage =
          result.message ||
          result.error ||
          'فشل في الإضافة';

        results.push({
          ...item,
          pno         : item.pno || result?.data?.pno || 'N/A',
          success     : false,
          message     : errorMessage,
          originalRow,
        });
      }
    } catch (error) {
      console.error(`[ERROR] Upload failed for item ${i + 1}/${mappedRows.length} (PNO: ${item.pno || 'N/A'}):`, error);
      results.push({
        ...item,
        pno         : item.pno || 'N/A',
        success     : false,
        message     : 'خطأ في الاتصال بالخادم',
        originalRow,
      });
    }
  }

  /* 5) إنهاء شريط التقدم */
  progressBarInner.style.width  = '100%';
  progressBarInner.textContent = '100%';

  /* 6) عرض النتائج مع headers */
  displayResults(results, headers);  // تأكد أن displayResults تستقبل headers وتعرضها في الأعلى

  /* 7) إخفاء الشريط */
  setTimeout(() => {
    progressBar.style.display     = 'none';
    progressBarInner.style.width  = '0%';
    progressBarInner.textContent  = '';
  }, 2000);

} catch (error) {
  console.error('[FATAL] Error during upload process:', error);
  showResponse('حدث خطأ أثناء معالجة الملف', 'error');
  progressBar.style.display = 'none';
}
}



function downloadFailedItemsReport(failedItems) {
  if (!failedItems || failedItems.length === 0) {
    showResponse('لا توجد عناصر فاشلة لتحميلها', 'info');
    return;
  }

  // Get all original headers from the first failed item
  const originalHeaders = failedItems[0].originalRow ? 
    Object.keys(failedItems[0].originalRow) : 
    [];

  // Create report data with all original columns plus error info
  const reportData = failedItems.map(item => {
    const rowData = {};
    
    // First add all original headers (even if empty)
    originalHeaders.forEach(header => {
      rowData[header] = item.originalRow ? 
        (item.originalRow[header] || '') : 
        '';
    });
    
    // Then add our error information columns
    return {
      ...rowData,
      'حالة العملية': item.success ? 'نجاح' : 'فشل',
      'رسالة الخطأ': item.message || 'لا توجد رسالة خطأ',
      'PNO المستخدم': item.pno || 'N/A'
    };
  });

  // Create worksheet with all columns in correct order
  const ws = XLSX.utils.json_to_sheet(reportData);
  
  // Reorder columns to put original headers first
  const newHeaders = [
    ...originalHeaders,
    'حالة العملية',
    'رسالة الخطأ', 
    'PNO المستخدم'
  ];
  
  // Reconstruct worksheet with correct column order
  const newWs = XLSX.utils.json_to_sheet(reportData, { header: newHeaders });
  
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, newWs, "العناصر الفاشلة");

  // Download file
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  XLSX.writeFile(wb, `العناصر_الفاشلة_${timestamp}.xlsx`);

  showResponse('تم تحميل تقرير العناصر الفاشلة بنجاح', 'success');
}

/**
* Read an .xlsx file in the browser, convert the first sheet to JSON,
* and map Arabic column names to English keys.
*
* @param {File} file         – the Excel file selected by the user
* @param {HTMLElement} bar   – the <div> acting as a progress bar
* @returns {Promise<Array>}  – array of mapped row objects
*/
function readExcelFile(file, bar) {
// header → field map
const HEADER_MAP = {
  'رقم الخاص'        : 'pno',
  'رقم الخاص المورد'  : 'source_pno',
  'اسم الصنف'        : 'itemname',
  'رقم الشركه'       : 'eitemname',
  'اسم الشركه'       : 'companyproduct',
  'الرقم الاصلي'     : 'oem_number',
  'الرقم الاصلي المكافي':'extrenal_oem',
  'الكمية'           : 'showed',          // quantity
  'سعر البيع'        : 'buyprice',
  'التخفيض'          : 'discount',
  'ملاحظات'          : 'json_description',
  'الفئة'            : 'category',
  'نوع التخفيض'      : 'discount_type',
  'فئة الصنف'      : 'category_type'    // remove extra leading spaces
};

// Arabic → English discount-type map
const DISCOUNT_TYPE_MAP = {
  'المحل'  : 'market',
  'المورد' : 'source'
};

return new Promise((resolve, reject) => {
  const reader = new FileReader();

  reader.onload = e => {
    try {
      const data      = new Uint8Array(e.target.result);
      const workbook  = XLSX.read(data, { type: 'array' });
      const sheet     = workbook.Sheets[workbook.SheetNames[0]];
      const rawRows   = XLSX.utils.sheet_to_json(sheet);   // [{رقم الخاص: "...", …}, …]

      // ---------- map headers & normalise discount_type ----------
      const mappedRows = rawRows.map(row => {
        const mapped = {};

        for (const [arabicKey, value] of Object.entries(row)) {
          const englishKey = HEADER_MAP[arabicKey.trim()] || arabicKey.trim(); // normalise header
          mapped[englishKey] = value;
        }

        // convert “discount_type” Arabic values → API values
        if (mapped.discount_type !== undefined && mapped.discount_type !== null) {
          const arabicType = String(mapped.discount_type).trim();
          mapped.discount_type = DISCOUNT_TYPE_MAP[arabicType] || arabicType;  // leave untouched if unknown
        }

        return mapped;
      });

      // update progress bar (half-way mark)
      bar.style.width = '50%';
      bar.textContent = '50 %';

      resolve({ rawRows, mappedRows });
    } catch (err) {
      console.error('[ERROR] Error reading Excel file:', err);
      reject(err);
    }
  };

  reader.onerror = err => {
    console.error('[ERROR] FileReader failed:', err);
    reject(err);
  };

  reader.readAsArrayBuffer(file);
});
}


function displayResults(results) {
const resultsBody = document.getElementById('results-body');
const bulkResults = document.getElementById('bulk-results');

resultsBody.innerHTML = '';

const failedItems = results.filter(item => !item.success);

results.forEach((result, index) => {
  const row = document.createElement('tr');
  let rowClass = 'table-danger';
  
  if (result.success) {
    if (result.message && result.message.includes('المنتج الموجود لديه نفس السعر أو سعر أفضل')) {
      rowClass = 'table-warning';
    } else if (result.message && result.message.includes('تم تحديث المنتج الحالي بسعر أقل')) {
      rowClass = 'table-warning';
    } else {
      rowClass = 'table-success';
    }
  }

  row.classList.add(rowClass);
  row.innerHTML = `
    <td>${index + 1}</td>
    <td>${result.pno || 'غير معروف'}</td>
    <td>${result.success ? 'نجاح' : 'فشل'}</td>
    <td>${result.message || ''}</td>
  `;
  resultsBody.appendChild(row);
});

const successCount = results.filter(r => r.success).length;
const totalCount = results.length;

// Add download failed items button if there are failures
if (failedItems.length > 0) {
  const downloadFailedBtn = document.createElement('button');
  downloadFailedBtn.className = 'btn btn-danger btn-sm mt-3';
  downloadFailedBtn.innerHTML = '<i class="fas fa-download me-2"></i>تحميل العناصر الفاشلة';
  downloadFailedBtn.onclick = () => downloadFailedItemsReport(failedItems);
  
  const summaryRow = document.createElement('tr');
  summaryRow.classList.add('table-info');
  summaryRow.innerHTML = `
    <td colspan="4" class="text-center">
      <strong>النتيجة النهائية: ${successCount}/${totalCount} (${Math.round((successCount / totalCount) * 100)}% نجاح)</strong>
      ${failedItems.length > 0 ? '<div class="mt-2"></div>' : ''}
    </td>
  `;
  
  const buttonCell = summaryRow.querySelector('td');
  buttonCell.appendChild(downloadFailedBtn);
  
  resultsBody.appendChild(summaryRow);
} else {
  const summaryRow = document.createElement('tr');
  summaryRow.classList.add('table-success');
  summaryRow.innerHTML = `
    <td colspan="4" class="text-center">
      <strong>النتيجة النهائية: ${successCount}/${totalCount} (100% نجاح)</strong>
    </td>
  `;
  resultsBody.appendChild(summaryRow);
}

bulkResults.style.display = 'block';
bulkResults.scrollIntoView({ behavior: 'smooth' });

if (failedItems.length > 0) {
  setTimeout(() => {
    downloadFailedItemsReport(failedItems);
  }, 1000);
}
}


}

function downloadTemplate() {
const templateData = [];

const itemNameList = ['فلتر زيت', 'زيت محرك', 'بطارية جافة', 'كشاف أمامي', 'إطار خلفي'];
const companyList = ['', 'febi'];
const categoryList = ['ألماني', 'كوري', 'أمريكي'];
const notesList = ['جودة ممتازة', 'صناعة أصلية', 'مناسب لجميع السيارات'];
const disctyp = ['المورد', 'المحل'];

// Map item names to item categories
const itemCategoryMap = {
  'فلتر زيت': 'فلتر',
  'زيت محرك': 'زيت',
  'بطارية جافة': 'بطارية',
  'كشاف أمامي': 'كهرباء',
  'إطار خلفي': 'إطارات'
};

for (let i = 1; i <= 10; i++) {
  const itemName = itemNameList[Math.floor(Math.random() * itemNameList.length)];
  templateData.push({
    'رقم الخاص': ``,
    'رقم الخاص المورد': `201-${i}`,
    'اسم الصنف': itemName,
    'اسم الشركه': companyList[Math.floor(Math.random() * companyList.length)],
    'الرقم الاصلي': `OEMtest-${20 + i}`,
    'الرقم الاصلي المكافي': `OEMtest-${20 + i}`,
    'رقم الشركه'  : `ABS${20 + i}`,
    'الكمية': Math.floor(Math.random() * 100),
    'سعر البيع': (10 + Math.random() * 40).toFixed(2),
    'التخفيض': (Math.random() * 0.2).toFixed(2),
    'ملاحظات': notesList[Math.floor(Math.random() * notesList.length)],
    'نوع التخفيض': disctyp[Math.floor(Math.random() * disctyp.length)],
    'الفئة': categoryList[Math.floor(Math.random() * categoryList.length)],
    'فئة الصنف': itemCategoryMap[itemName] || 'أخرى'
  });
}

const ws = XLSX.utils.json_to_sheet(templateData);
const wb = XLSX.utils.book_new();
XLSX.utils.book_append_sheet(wb, ws, "العناصر");

XLSX.writeFile(wb, "نموذج_العناصر.xlsx");

showResponse('تم تحميل النموذج بنجاح', 'success');
}





  
  function showResponse(message, type) {
    const responseDiv = document.getElementById("response");
    responseDiv.textContent = message;
    responseDiv.className = `response-message ${type}`;
    responseDiv.style.display = "block";
    
    // Hide after 5 seconds
    setTimeout(() => {
      responseDiv.style.display = "none";
    }, 5000);
  }