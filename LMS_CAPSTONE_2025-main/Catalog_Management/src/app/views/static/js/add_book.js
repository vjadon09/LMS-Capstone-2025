function previewImage(event) {
    const imagePreview = document.getElementById('imagePreview');
    const file = event.target.files[0];
    
    if (file) {
        // Create a URL for the selected image file
        const reader = new FileReader();
        reader.onload = function() {
            imagePreview.src = reader.result;  // Set the source of the preview image
            imagePreview.style.display = 'block';  // Display the image
        }
        reader.readAsDataURL(file);  // Read the image file as data URL
    }
}

function cancel(){
    location.href = "/catalog/edit_inventory";
}

function clear() {
    document.getElementById("addBookForm").reset();

    const imagePreview = document.getElementById('imagePreview');
    imagePreview.src = "";
    imagePreview.style.display = 'none';
    const imageUpload = document.getElementById('imageUpload');
    imageUpload.value = '';

    const fileSection = document.getElementById('fileUploadSection');
    fileSection.style.display = 'none';
    const bookFile = document.getElementById('bookFile');
    bookFile.value = '';

}

function validateForm() {
    let isValid = true;
    const errorMessage = "This field is required";

    const format = document.getElementById("format").value;
    const pageNumber = document.getElementById("pageNumber");
    const numOfMins = document.getElementById("numOfMins");

    // Check that at least one of the fields is filled (pageNumber or numOfMins)
    if (format === "eBook" && !pageNumber.value.trim()) {
        isValid = false;
        if (!document.getElementById(pageNumber.id + "-error")) {
            const error = document.createElement('div');
            error.id = pageNumber.id + "-error";
            error.classList.add('text-danger', 'mt-2');
            error.textContent = errorMessage;
            pageNumber.parentElement.appendChild(error);
        }
    } else if (format === "Audio" && !numOfMins.value.trim()) {
        isValid = false;
        if (!document.getElementById(numOfMins.id + "-error")) {
            const error = document.createElement('div');
            error.id = numOfMins.id + "-error";
            error.classList.add('text-danger', 'mt-2');
            error.textContent = errorMessage;
            numOfMins.parentElement.appendChild(error);
        }
    } else {
        // Remove any previous errors for these fields
        if (format === "eBook" && document.getElementById(pageNumber.id + "-error")) {
            document.getElementById(pageNumber.id + "-error").remove();
        }
        if (format === "Audio" && document.getElementById(numOfMins.id + "-error")) {
            document.getElementById(numOfMins.id + "-error").remove();
        }
    }

    const formFields = document.querySelectorAll('#addBookForm input[required], #addBookForm textarea[required], #addBookForm select[required]');

    formFields.forEach(field => {
        const errorElement = document.getElementById(field.id + "-error");
        
        if (field.tagName.toLowerCase() === "select") {
            if (!field.value || field.value === "" || field.value === "Choose...") {
                isValid = false;
                if (!errorElement) {
                    const error = document.createElement('div');
                    error.id = field.id + "-error";
                    error.classList.add('text-danger', 'mt-2');
                    error.textContent = errorMessage;
                    field.parentElement.appendChild(error);
                }
            } else {
                if (errorElement) {
                    errorElement.remove();
                }
            }
        } else {
            if (!field.value.trim()) {
                isValid = false;
                if (!errorElement) {
                    const error = document.createElement('div');
                    error.id = field.id + "-error";
                    error.classList.add('text-danger', 'mt-2');
                    error.textContent = errorMessage;
                    field.parentElement.appendChild(error);
                }
            } else {
                if (errorElement) {
                    errorElement.remove();
                }
            }
        }
    });

    return isValid;
}

function submitBook(event) {
    event.preventDefault();
    const formIsValid = validateForm();
    if (formIsValid) {
        const formData = new FormData(document.getElementById("addBookForm"));
        
        // Set pageNumber or numOfMins to 0 if they are empty
        for (let [key, value] of formData.entries()) {
            if ((key === "numOfMins" || key === "pageNumber") && (value === "" || value == null)) {
                formData.set(key, 0);
            }
        }

        // Check book cover uploaded correctly
        const fileInput = document.getElementById('imageUpload');
        const file = fileInput.files[0];
        let bookCoverValid = false;

        if (file) {
            if (!['image/jpeg', 'image/png'].includes(file.type)) {
                alert('Only JPG, PNG, or JPEG images are allowed for the book cover!');
                event.target.value = '';
                imagePreview.style.display = 'none';
                return;
            }
            const reader = new FileReader();
            reader.onloadend = function() {
                //formData.append('image', reader.result);
                bookCoverValid = true; // Mark the book cover as valid once it’s read
                // After both files are ready, submit the form data
                checkAndSubmitFormData(formData);
            };
            reader.readAsDataURL(file);
        } else {
            // If no book cover file selected
            alert("A book cover file must be selected!");
            return;
        }

        // Check the format of the book and ensure the book file is valid
        const bookFileInput = document.getElementById('bookFile');
        const bookFile = bookFileInput.files[0];
        const format = document.getElementById("format").value;
        let bookFileValid = false;

        if (bookFile) {
            if (format === "eBook" && bookFile.type !== "application/epub+zip") {
                alert('Only EPUB files are allowed for eBooks!');
                return;
            } else if (format === "Audio" && bookFile.type !== "audio/mp3") {
                alert('Only MP3 files are allowed for Audio books!');
                return;
            }
            const bookreader = new FileReader();
            bookreader.onloadend = function() {
                //formData.append('bookFile', bookreader.result);
                bookFileValid = true;
                // After both files are ready, submit the form data
                checkAndSubmitFormData(formData);
            };
            bookreader.readAsDataURL(bookFile);
        } else {
            // If no book file selected
            alert("A book file must be selected!");
            return;
        }

        // Check and submit the form data once both files are validated and loaded
        function checkAndSubmitFormData(formData) {
            if (bookCoverValid && bookFileValid) {
                submitFormData(formData);
            }
        }
    }
}

async function submitFormData(formData) {
    var myModal = new bootstrap.Modal(document.getElementById('successModal'));
    try {
        const response = await fetch('/catalog/add-item', {
            method: 'POST',
            body: formData
        });

        if (response.status === 409) {
            document.getElementById('modal-body').innerHTML = formatModal(true);
            myModal.show();
            const result = await response.json();
            console.log(result.detail);
            return;
        }

        if (response.ok) {
          document.getElementById('modal-body').innerHTML = formatModal(false);
          myModal.show();
          const closeButton = document.querySelector('.btn-close');
          closeButton.addEventListener('click', function () {
            document.getElementById("addBookForm").reset();
            if (response.redirected) {
                window.location.href = response.url;
            }
        });
        } else {
            document.getElementById('modal-body').innerHTML = formatModal(true);
            myModal.show();
            console.log("An unexpected error occurred.");
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

function toggleFileUpload() {
    const format = document.getElementById("format").value;
    const fileUploadSection = document.getElementById("fileUploadSection");
    const bookFile = document.getElementById("bookFile");

    if (format === "eBook" || format === "Audio") {
        fileUploadSection.style.display = "block";

        if (format === "eBook") {
            bookFile.accept = ".epub";
        } else if (format === "Audio") {
            bookFile.accept = ".mp3";
        }
    } else {
        fileUploadSection.style.display = "none";
        bookFile.value = "";
    }

    // Toggle the page number or minutes fields
    const pageField = document.getElementById('pageField');
    const minuteField = document.getElementById('minuteField');
    
    if (format === 'eBook') {
      pageField.style.display = 'block';
      minuteField.style.display = 'none';
    } else if (format === 'Audio') {
      pageField.style.display = 'none';
      minuteField.style.display = 'block';
    }
}

function formatModal(error){
  let modalBody;
  if (error){
    modalBody = `<div class="row"><p class="text-center" style="font-size: 40px;">❎</p></div>
                <div class="row"><p class="text-center fs-5">Form submission failed!</p></div>
                <div class="row"><p class="text-center">Please try again.</p></div>`
    
  } else{
    modalBody = `<div class="row"><p class="text-center" style="font-size: 40px;">✅</p></div>
                <div class="row"><p class="text-center fs-5">Successfully submited!</p></div>`
  }
  return modalBody
}


document.getElementById("addBookForm").addEventListener("submit", submitBook);
document.querySelector('.btn-clear-size').addEventListener('click', clear);
document.querySelector('.btn-cancel-size').addEventListener('click', cancel);