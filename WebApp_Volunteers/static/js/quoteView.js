class QuoteView {
    constructor(model) {
        // The bind() method creates a new function that, when called, has its this keyword set to the provided value.
        model.subscribe(this.redrawList.bind(this));
    }
    redrawList(archive) {
        let body = document.getElementById("quote-section");
        body.innerHTML = "";
        for (let item of archive.newItems) {
            this.addCard(item, body);          
        }
    }
    addCard(item, parent) {
        let editable = false, deleteable = true;
        let edit_enabled = editable ? 'enabled' : 'disabled';
        let delete_enabled = deleteable ? 'enabled' : 'disabled';
        
        let card = item.createDivCard();
        card.innerHTML += 
                        `<button class="edit" onclick="allModel.editItem(this)" ${edit_enabled}>Edit Card</button>
                         <button class="delete" onclick="allModel.deleteItem(this)" ${delete_enabled}>Delete Card</button>`;
        parent.append(card);
    }
}