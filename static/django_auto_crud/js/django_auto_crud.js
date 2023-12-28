// Gets the element with the class "preloader".
let preloader = document.querySelector('.preloader');

// Function to show the preloader
function showPreloader() {
    // Checks if the element exists before adding the event
    if (preloader) {
        // Sets the preloader to be visible
        preloader.style.height = '100%';

        // Sets a timeout to show the preloader
        setTimeout(function () {
            let preloaderChildren = preloader.children;

            for (let i = 0; i < preloaderChildren.length; i++) {
                preloaderChildren[i].style.display = 'block';
            }
        }, 200);
    }
}

// Function to hide the preloader
function hidePreloader() {
    // Checks if the element exists before adding the event
    if (preloader) {
        // Sets the preloader to be hidden
        preloader.style.height = '0%';

        // Sets a timeout to hide the preloader
        setTimeout(function () {
            let preloaderChildren = preloader.children;

            for (let i = 0; i < preloaderChildren.length; i++) {
                preloaderChildren[i].style.display = 'none';
            }
        }, 200);
    }
}

// Function to navigate back to the previous page
function goBackOrNavigate(url = null) {
    showPreloader();

    if (url) {
        // Function to navigate to the URL
        window.location.href = url;
    } else {
        // Function to navigate back to the previous page
        window.history.back();
    }
}

// Gets the element with the ID "backButton".
let backButton = document.getElementById('backButton');

// Checks if the element exists before adding the event
if (backButton) {
    // Gets the URL from the element
    let url = backButton.dataset.url;
    // Adds the event to the element
    backButton.addEventListener('click', function () {
        goBackOrNavigate(url);
    });
}

// Select all <a> elements with a href attribute that is not empty and not equal to "#"
let elementsWithUrl = document.querySelectorAll('a[href]:not([href=""]):not([href="#"])');

// Add the event to each selected element
elementsWithUrl.forEach(function (element) {
  element.addEventListener('click', showPreloader);
});

// Select all forms
let forms = document.querySelectorAll('form');

// Add the event to each form
forms.forEach(function (form) {
  form.addEventListener('submit', showPreloader);
});