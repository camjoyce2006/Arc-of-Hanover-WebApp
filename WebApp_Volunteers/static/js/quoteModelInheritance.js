'use strict';
class Subject {

    constructor() {
        this.handlers = [];
    }

    subscribe(fn) {
        this.handlers.push(fn);
    }

    unsubscribe(fn) {
        this.handlers = this.handlers.filter(
            function(item) {
                if (item !== fn) {
                    return item;
                }
            }
        );
    }

    publish(msg, someobj) {
        var scope = someobj || window;
        for (let fn of this.handlers) {
            fn(scope, msg);
        }
    }
}

class Archive extends Subject {
    constructor(name) {
        super();
        this.name = name;
        this.newItems = [];
    }

    addItem(it) {
        this.newItems.push(it);
        this.publish(`New ${it.type} added to Archive ${this.name}`, this);
    }

    editItem(button) {
        let card = button.parentElement;
        let obj;
        for(let item of this.newItems) {
            if(item.id == card.id) {
                obj = item;
            }
        }
        switch(obj.type) {
            case 'Bible Verse':
                generateInputFields('Bible Verse');
                let inputs = document.querySelectorAll('input.bible, textarea.bible');
                let vals = [obj.verse, obj.book, obj.translation];
                let i = 0;
                for(let field of inputs) {
                    let objId = field.id;
                    console.log(`${objId}: ${vals[i]}`);
                    field.value = vals[i];
                    i++;  
                }
                document.getElementById('kind').value = 'Bible Verse';
                let saveButton = document.getElementById('save')
                saveButton.removeAttribute('onclick');
                saveButton.innerText = `Save Changes to Verse ${obj.id.substring(obj.id.indexOf("-") + 1)}`;
                saveButton.addEventListener("click", cont);
                function cont() {
                    obj.verse = inputs[0].value;
                    obj.book = inputs[1].value;
                    obj.translation = inputs[2].value;

                    allModel.publish(`Edited ${obj.id} (${obj.book})`, allModel);
                    allLss.saveAll(allModel);
                    saveButton.setAttribute('onclick',  `getInputs();`);
                    saveButton.innerText = 'Add Quote Card';
                    saveButton.removeEventListener('click', cont);
                }
                break;
        }
    }

    deleteItem(button) {
        let card = button.parentElement;
        for(let item of this.newItems) {
            if(item.id == card.id) {
                console.log(`Card ID: ${card.id}`);
                console.log(`Archive: ${this.name}`)
                this.newItems.splice(this.newItems.indexOf(item), 1);
                this.publish(`Deleted ${item.id} from Archive ${this.name}`, this);
                if(item.type == "Bible Verse") {
                    console.log(!!item.verse ? item.verse:"empty");
                    bibleModel.deleteItem(button);
                } else {
                    quoteModel.deleteItem(button);
                }
            }
        }
        card.remove();
        allModel.decrementItems();
        quoteLss.saveAll(quoteModel);
        bibleLss.saveAll(bibleModel);
        allLss.saveAll(allModel);
    }

    displayCards() {
        console.log(`Loading ${this.name}...`);
        this.publish(`Displaying cards in Archive ${this.name}`, this);
    }
}

class QuoteModel extends Archive {
    constructor(name) {
        super();
        this.name = name;
        this.verses = 0;
        this.quotes = 0;
        this.items = 0;
    }

    incrementItems() {
        this.items++;
    }

    decrementItems() {
        this.items--;
    }

    getId() {
        return this.id;
    }

    equals(id) {
        return this.id == id;
    }
}

class RegularQuote {
    constructor(quote, author) {
        console.log('reg')
        this.quote = quote;
        this.author = author;
        this.type = "regQuote";
        this.id = `quote-${quoteModel.items++}`;
        this.vals = ['quote', 'author', 'type', 'id'];
    }

    toString() {
        return `"${this.quote}" -${this.author}`;
    }

    createDivCard() {
        let card = document.createElement('div');
        card.classList.add('inspire');
        card.id = this.id;
        card.innerHTML = 
                        `<p class="quote-box">"${this.quote}"</p>
                         <p class="book-ref">${this.author}</p>`;
        return card;
    }
}

class DocumentQuote extends RegularQuote {
    constructor(quote, author, source) {
        super(quote, author);
        this.source = source;
        this.vals = ['quote', 'author', 'source', 'type', 'id'];
        this.type = "docQuote";
        //this.year = year;
    }

    toString() {
        return `"${this.quote}" -${this.author} (${this.source})`;
    }

    createDivCard() {
        let card = document.createElement('div');
        card.classList.add('inspire');
        card.id = this.id;
        card.innerHTML = 
                `<p class="quote-box">"${this.quote}"</p>
                 <p class="book-ref">${this.author} (${this.suorce})</p>`;
        return card;
    }
}

class BibleVerse extends DocumentQuote {
    constructor(verse, book, translation) {
        super(verse, book, translation);
        this.type = "Bible Verse";
        this.id = `verse-${bibleModel.items++}`;
    }

    toString() {
        return `${this.author} ${this.source} - ${this.quote}`;
    }

    createDivCard() {
        let card = document.createElement('div');
        card.classList.add('verse');
        card.id = this.id;
        card.innerHTML = 
                    `<p class="quote-box">"${this.quote}"</p>
                     <p class="book-ref">${this.author} ${this.source}</p>`;
        return card;
    }
}