import React, { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';

import { useState } from 'react';


/**
 * @returns a complete inpiut form
 */
function InputForm({ kind }) {
    const [cardType, setCardType] = useState(kind);
    const [action, setAction] = useState('add');

    return (
            <div id="input-fields">
                <SelectKind cardType={cardType} onCardTypeChange={setCardType} />
                <InputFields selectValue={cardType} />
                <SubmitForm cardType={cardType} action={action} onActionChange={setAction} />
            </div>
    );
}

/**
 * @param {*} param0 a cardType prop to generate inputs for and a prop that is called when cardType is modified
 * @returns a select dropdown for which card type to input
 */
function SelectKind({ cardType, onCardTypeChange }) {
    return (
            <form>
                <label htmlFor="kind">Type of quote</label>
                <select id="kind" defaultValue={cardType} onChange={(e) => onCardTypeChange(e.target.value)}>
                    <option value="" hidden disabled>Select a type of quote</option>
                    <option value="Bible Verse">Bible Verse</option>
                    <option value="Quote">Quote</option>
                </select>
            </form>
    )
}

/**
 * @param {*} selectValue the value from the select dropdown SelectKind
 * @returns the input fields for the selected cardType
 */
function InputFields({ selectValue }) {
    var classList = ["input"], labelNames = [];
    switch(selectValue){
        case 'Bible Verse':
            labelNames = ["Verse", "Book", "Translation"];
            classList.splice(classList.indexOf("quote"), 0, "bible");
            break;
        case 'Quote':
            labelNames = ["Quote", "Author", "Source"];
            classList.splice(classList.indexOf("bible"), 0, "quote");
            break;
        default:
            return; 
    }

    let classes = "";
    classList.forEach((c) => classes += c + " ");
 
    return (
        <div className={`${classList[0]}-inputs`}>
            <label htmlFor={labelNames[0].toLowerCase()} className={classes}>{labelNames[0]} </label>
            <textarea className={classes} id={labelNames[0].toLowerCase()} placeholder={`Type ${labelNames[0].toLowerCase()} here`}></textarea>
            <label htmlFor={labelNames[1].toLowerCase()} className={classes}>{labelNames[1]} </label>
            <input type="text" className={classes} id={labelNames[1].toLowerCase()} placeholder={`Type ${labelNames[0].toLowerCase()} here`}></input>
            <label htmlFor={labelNames[2].toLowerCase()} className={classes}>{labelNames[2]} </label>
            <input type="text" className={classes} id={labelNames[2].toLowerCase()} placeholder={`Type ${labelNames[0].toLowerCase()} here`}></input>
        </div>
    );
}

/**
 * 
 * @param {*} cardType the type of card being added
 * @returns a button to submit the form
 */
function SubmitForm({ cardType }) {
    function submitForm(action) {
        let labelNames = (cardType == 'Bible Verse') ? ["Verse", "Book", "Translation"] : ["Quote", "Author", "Source"];        
        if(!!document.getElementById(labelNames[0].toLowerCase())) {
            let q = document.getElementById(labelNames[0].toLowerCase()).value;
            let a = document.getElementById(labelNames[1].toLowerCase()).value;
            let s = document.getElementById(labelNames[2].toLowerCase()).value;
            let t = (cardType == 'Bible Verse') ? 'Verse' : 'Quote';
            let newCard = {quote: q, author: a, source: s, type: t};
            console.log(newCard);
            if(action == "add") addCard(newCard);
            else if(action == "edit") return newCard;
            console.log(CARDS);
            reGenerateCards();
            //return newCard;
        } else return;
    }
    return (
    <button onClick={() => submitForm("add")} id="save">Save {cardType} Card</button>
    )

}

/**
 * 
 * @param {*} param0 the quote, author and source of a quote
 * @returns a dv card with the provided information
 */
function QuoteCard({ quote, author, source, quoteID }) {
    return (
        <div className="inspire" id={quoteID}>
            <p className="quote-box">"{quote}"</p>
            <p className="book-ref">{author} ({source})</p>
            <CardActions cards={CARDS} cardIndex={quoteID} />
        </div>
    )
}

function BibleVerseCard({ verse, book, translation, verseID }) {
    return (
        <div className="verse" id={verseID}>
            <p className="quote-box">"{verse}"</p>
            <p className="book-ref">{book} {translation}</p>
            <CardActions cards={CARDS} cardIndex={verseID} />
        </div>
    );
}

function CardActions({ cards, cardIndex }) {
    let editable = true, deleteable = false;
    let edit_enabled = !editable ? 'enabled' : 'disabled';
    let delete_enabled = !deleteable ? 'enabled' : 'disabled';
    return (
        <div className="card-actions">
            <button className="edit" onClick={() => editCard(cardIndex)} disabled={false}>Edit Card</button>
            <button className="delete" onClick={() => deleteCard(cardIndex)} disabled={false}>Delete Card</button>
        </div>
    );
}

function FilterableCardContainer({ cards }) {
    const [filterType, setFilterType] = useState('showAll');
    const [hideInputs, setHideInputs] = useState('Hide Inputs');
    const [fullQuotes, setFullQuotes] = useState('Show Full Quotes');

    return (
        <div>
            <CardFilterer 
                filterType={filterType}
                onFilterTypeChange={setFilterType}
                hideInputs={hideInputs}
                onHideInputsChange={setHideInputs}
                fullQuotes={fullQuotes}
                onFullQuotesChange={setFullQuotes} />
            <CardContainer 
                cards={cards}
                filterType={filterType} />
        </div>
    );
}

function CardFilterer({ filterType, onFilterTypeChange, hideInputs, onHideInputsChange, fullQuotes, onFullQuotesChange }) {
    return (
        <h1>Quote Catalog
            <button id="inputDisplay" onClick={() => {
                    onHideInputsChange(`${(hideInputs == 'Hide Inputs') ? 'Show' : 'Hide'} Inputs`);
                    if(hideInputs == 'Hide Inputs') document.getElementById('input-container').style.display = 'none';
                    else document.getElementById('input-container').removeAttribute('style');
                }}>
                {hideInputs}
            </button>
            <button id="full-quotes" onClick={(e) => {
                    onFullQuotesChange(`${(fullQuotes == 'Hide Full Quotes') ? 'Show' : 'Hide'} Full Quotes`);
                    console.log(e.target.innerText);
                }}>
                {fullQuotes}
            </button>
            <ul id="filters" name={filterType}>
                <li><button id="showVerses" className="filter" onClick={(e) => onFilterTypeChange(e.target.id)}>Bible Verses</button></li>
                <li><button id="showQuotes" className="filter" onClick={(e) => onFilterTypeChange(e.target.id)}>Quotes</button></li>
                <li><button id="showAll" className="filter" onClick={(e) => onFilterTypeChange(e.target.id)}>All Items</button></li>
            </ul>
        </h1>  
    );
}

function CardContainer({ cards, filterType }) {
    let content = [];

    cards.forEach((card) => {
        if((card.type == "Verse" && filterType !== 'showQuotes')) {
            content.push(
                <BibleVerseCard verse={card.quote} book={card.author} translation={card.source} verseID={cards.indexOf(card)} key={`Verse-${cards.indexOf(card)}`}/>
            );
        } else if((card.type == "Quote" && filterType !=='showVerses')) {
            content.push(
                <QuoteCard quote={card.quote} author={card.author} source={card.source} quoteID={cards.indexOf(card)} key={`Quote-${cards.indexOf(card)}`} />
            );
        } else return;
    })   

    return (
        <div id="quote-section">{content}</div>
    );
}

var CARDS = [
    {quote: "I am the way and the truth and the life", author: "John 14:6", source: "", type: "Verse"},
    {quote: "Hello", author: "Me", source: "none", type: "Quote"}
];

function addCard(newCard) {
    CARDS.push(newCard);
    localStorage.setItem("quotes", JSON.stringify(CARDS));
}

function deleteCard(cardIndex) {
    CARDS.splice(Number.parseInt(cardIndex), 1);
    localStorage.setItem("quotes", JSON.stringify(CARDS));
    reGenerateCards();
}

function editCard(cardIndex) {
    let cardToEdit = CARDS[Number.parseInt(cardIndex)];
    let labelNames = (cardToEdit.type == 'Verse') ? ["Verse", "Book", "Translation"] : ["Quote", "Author", "Source"];
    generateInputs((cardToEdit.type == 'Verse') ? 'Bible Verse' : 'Quote');
    console.log(cardToEdit.type);
    document.getElementById(labelNames[0].toLowerCase()).value = cardToEdit.quote;
    document.getElementById(labelNames[1].toLowerCase()).value = cardToEdit.author;
    document.getElementById(labelNames[2].toLowerCase()).value = cardToEdit.source;
    document.getElementById('save').onclick = `submitForm("edit")`;

    const editedCard = document.getElementById('save').click();

    let newCard = async () => {
        const e = await editedCard;
        return e;
    };
    CARDS[Number.parseInt(cardIndex)] = newCard;
    localStorage.setItem("quotes", JSON.stringify(CARDS));
}

const cardSection = createRoot(document.getElementById('quote-container'));
const inputs = createRoot(document.getElementById('input-container'));

function reGenerateCards() {
    var App = function App() {
        let lssCards = localStorage.getItem("quotes");
        if(!!lssCards) {
            CARDS = JSON.parse(lssCards);

            CARDS.forEach((c) => {
                if(c === null) CARDS.splice(CARDS.indexOf(c), 1);
            });
        localStorage.setItem("quotes", JSON.stringify(CARDS));
        return <FilterableCardContainer cards={CARDS} />
    }
}

    cardSection.render(
        <StrictMode>
            <App />
        </StrictMode>
    );
}

function generateInputs(kind) {
    inputs.render(
        <StrictMode>
            <InputForm kind={kind} />
        </StrictMode>
    )
    }

document.body.onload = () => {
    reGenerateCards(); 
    generateInputs("");
}