    
//document.getElementById('inputDisplay').onclick = 'displayInputs(this)';

function displayControlButton(button) {
    let inputDiv = document.getElementById('input-fields');
    switch(button.innerText) {
        case 'Hide Inputs':
            button.innerText = 'Show Inputs';
            inputDiv.style.display = 'none';
            break;
        default:
            button.innerText = 'Hide Inputs';
            inputDiv.removeAttribute('style');
    }

}