const forms = document.querySelectorAll('form');
const _form = forms[0];

Array.from(_form.elements).forEach((input) => {
    console.log(input);
});
// Select the form fields
var formFields = document.querySelectorAll('.form-group');

// Create a new div element
var wrapper = document.createElement('div');

// Set the wrapper's class name and attributes
wrapper.className = 'form-fields-wrapper';
wrapper.setAttribute('data-type', 'crispy');

// Loop through the form fields and append them to the wrapper
formFields.forEach(function(field) {
    wrapper.appendChild(field);
});

// Replace the original form fields with the wrapper
var form = document.querySelector('form');
form.innerHTML = '';
form.appendChild(wrapper);

var inputElement = document.getElementById("id_item_one");
inputElement.classList.add("col-md-6");
var inputElement = document.getElementById("id_item_one_unit_price");
inputElement.classList.add("col-md-2");
var inputElement = document.getElementById("id_item_one_quantity");
inputElement.classList.add("col-md-2");