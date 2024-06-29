"use strict"
class LocalStorageSaver {

    constructor(model,lsname) {
        this.lsname = lsname;
        let self = this;
        model.subscribe(function(slist, msg) {
            self.saveAll(slist);
        })
        // now restore from localstorage
        let restore_list = JSON.parse(localStorage.getItem(self.lsname));
        var obj = "";
        if(!!restore_list) {   
            console.log(`Restoring Archive ${model.name} from LocalStorage ${this.lsname}...` )
            console.log(restore_list)
            for(let vals of restore_list) {
                switch(vals.type) {
                    case "Bible Verse":
                        obj = new BibleVerse(vals.quote, vals.author, vals.source);
                        break;
                    case "regQuote":
                        obj = new RegularQuote(vals.quote, vals.author);
                        break;
                    case "docQuote":
                        obj = new DocumentQuote(vals.quote, vals.author, vals.source);
                        break;
                }
                console.log(`New ${obj.type}`); 
                model.addItem(obj);
            }
            console.log(`Successfully restored Archive ${model.name} from LocalStorage ${this.lsname}.` )
            console.log(model.newItems)
        }
    }
    saveAll(slist) {
        let ls_list = JSON.stringify(slist.newItems);
        localStorage.setItem(this.lsname, ls_list);
    }
}