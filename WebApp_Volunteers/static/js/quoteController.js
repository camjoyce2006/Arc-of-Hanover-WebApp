var typesTracked = ['Bible Verse', 'Quote']; //, 'JSON Upload'];

window.onload = function() {
    generateInputFields('');
    populateSelect('kind', typesTracked, 'Select a type quote');
}

var quoteModel = new QuoteModel("Quote");
var quoteView = new QuoteView(quoteModel);
var quoteLss = new LocalStorageSaver(quoteModel, "Quotes");
var bibleModel = new QuoteModel("Bible");
var bibleView = new QuoteView(bibleModel);
var bibleLss = new LocalStorageSaver(bibleModel, "BibleVerses");
var allModel = new QuoteModel("Alls");
var allView = new QuoteView(allModel);
var allLss = new LocalStorageSaver(allModel, "All");

/*function isMatch(inputBox, errorBox) {
    if(inputBox.value.match(inputBox.pattern) || inputBox.value == '') {
        inputBox.style.borderColor = "";
        document.getElementById(errorBox).style.display = "none";
    } else {
        console.log("no match: " + inputBox.id);
        inputBox.style.borderColor = "red";
        document.getElementById(errorBox).style.display = "block";
        document.getElementById(errorBox).innerText = inputBox.title;
        document.getElementById(errorBox).style.color = "red";        
    }
}*/

function generateInputFields(kind) {
    console.log(!!getKind() ? kind:'No Kind Selected');
    switch(kind) {
        case "Quote":
            document.getElementById('quote-inputs').removeAttribute('style');
            document.getElementById('bible-inputs').style.display = 'none';
            document.getElementById('json-inputs').style.display = 'none';
            break;
        case "Bible Verse":
            document.getElementById('quote-inputs').style.display = 'none';
            document.getElementById('bible-inputs').removeAttribute('style');
            document.getElementById('json-inputs').style.display = 'none';
            break;
        case "JSON Upload":
            document.getElementById('quote-inputs').style.display = 'none';
            document.getElementById('bible-inputs').style.display = 'none';
            document.getElementById('json-inputs').removeAttribute('style');
        break;
        case '':
            document.getElementById('quote-inputs').style.display = 'none';
            document.getElementById('bible-inputs').style.display = 'none';
            document.getElementById('json-inputs').style.display = 'none';
            break;
    }
}

function getKind() {
    return document.getElementById('kind').value;
}

function getInputs() {
    function toVals(rowcolids) {        
        let vals = {};
        for (let cid of rowcolids) {
            vals[cid] = document.getElementById(cid).value;
        }
        console.log(vals);
        return vals;
    }
    console.log("clicked");
    let vals, it;
    switch(getKind()) {
        case "Bible Verse":
            vals = toVals(['verse', 'book', 'translation']);
            it = new BibleVerse(vals.verse, vals.book, vals.translation);
            bibleModel.addItem(it);
            allModel.addItem(it);
            break;
        case "Quote":
            vals = toVals(['quote', 'author', 'source']);
            if (!vals.source) it = new RegularQuote(vals.quote, vals.author);
            else it = new DocumentQuote(vals.quote, vals.author, vals.source);
            quoteModel.addItem(it);
            allModel.addItem(it);
            break;
        case "JSON Upload":
            let json = document.getElementById('jsonobj').value;
            console.log(`JSON String: ${json}`)
            let list = JSON.parse(json);
            console.log(`Parsed JSON: ${list})`)
            localStorage.setItem('All', json);
            allLss.saveAll(allModel);
            break;
    }
}

function deleteAllEntries() {
    bibleModel.newItems = [];
    quoteModel.newItems = [];
    allModel.newItems = [];
    document.getElementById("quote-section").innerHTML = "";
    bibleLss.saveAll(bibleModel);
    quoteLss.saveAll(quoteModel);
    allLss.saveAll(allModel);
}

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

function showFullQuotes() {
    let allCards = document.querySelectorAll('#quote-section > div');
    let button = document.getElementById('full-quotes');
    let hidden = true;
    switch(button.innerText) {
        case 'Show Full Quotes':
            button.innerText = 'Hide Full Quotes';
            hidden = true;
            break;
        case 'Hide Full Quotes':
            button.innerText = 'Show Full Quotes';
            hidden = false;
            break;
    }
    allCards.forEach((card) => {
        if(hidden) {
            card.style = 'height: auto; min-height: 110px;';
            card.firstChild.style.overflow = 'visible';
            card.firstChild.style.height = 'auto';
            card.firstChild.style.display = 'flex';
        }
        else {
            card.removeAttribute('style');
            card.firstChild.removeAttribute('style');
        }
    });
}

function clearAll() {
    let inputs = document.querySelectorAll('#input-fields > div > :is(input, textarea)');
    inputs.forEach((item) => {
        item.value = '';
    })
}

function populateSelect(selectId, sList, msg) {
    let sel = document.getElementById(selectId, sList);
    sel.innerHTML = `<option value="" disabled selected hidden>${msg}</option>`;
    for (let s of sList) {
        sel.innerHTML += `<option value="${s}">${s}</option>`;;
    }
}
