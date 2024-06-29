'use strict';
class QuoteModel {
    constructor() {
        super();
        this.id = 0;
    }

    equals(id) {
        return this.id == id;
    }
}

class BibleVerse extends QuoteModel {
    constructor(verse, book, translation) {
        super();
        this.verse = verse;
        this.book = book;
        this.translation = translation;
        this.vals = ['verse', 'book', 'translation', 'type', 'id'];
        this.type = "Bible Verse";
        this.id = "verse-";
    }

    toString() {
        return "" + this.book + " " + this.translation + " - " + this.verse;
    }
}

class InspirationalQuote extends QuoteModel {
    constructor(quote, author, source) {
        super();
        this.quote = quote;
        this.author = author;
        //this.year = year;
        this.source = source;
        switch(source) {
            case source != "":
                this.vals = ['quote', 'author', 'source', 'type', 'id'];
                this.type = "regQuote";
                break;
            default:
                this.vals = ['quote', 'author', 'source', 'type', 'id'];
                this.type = "docQuote";
        }
        this.id = "quote-";
    }
}

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
        this.verses = 0;
        this.quotes = 0;
    }

    addItem(it) {
        
        switch(it.type) {
            case "Bible Verse":
                it.id += ++this.verses;
                break;
            case "docQuote": case "regQuote":
                it.id += ++this.quotes;
                break;
        }
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
        quoteLss.saveAll(quoteModel);
        bibleLss.saveAll(bibleModel);
        allLss.saveAll(allModel);
    }

    displayCards() {
        console.log(`Loading ${this.name}...`);
        this.publish(`Displaying cards in Archive ${this.name}`, this);
    }
    
    removeDuplicates() {
        let items = this.newItems;
        for(let item of items) {
            for(let i = 0; i < items.length - 1; i++) {
                if(items[i].cell == items[i+1].cell) {
                    items.splice(i, 1);
                }
            }
            if(items.length > 1 && (items[items.length - 2].cell == items[items.length - 1].cell)) {
                items.splice(items.length - 1, 1);
            }
        }
    }
}