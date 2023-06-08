'use strict';


class DialogModal extends HTMLElement {
    constructor(){
        super();
        this.shadow = this.attachShadow({mode: 'open'});
        this.shadow.innerHTML = `{% block html %}{% endblock %}`;
        // Add a click event on various child elements to close the parent modal
        (this.shadow.querySelectorAll('modal-card-foot .is-success, .modal-card-foot .is-danger') || []).forEach(($close) => {
            $close.addEventListener('click', () => {
              this.shadow.querySelector('.modal').classList.remove('is-active');
            });
        });
        this.shadow.querySelector('.modal').hidden = false;
    }
    async open(header,content,truthy,falsy){
        // Zeigt das Modal mit den entsprechenden Texten an. Promise wird true wenn der linke Button gedrückt wird, sonst false
        this.shadow.querySelector('.modal-card-title').innerText = header;
        this.shadow.querySelector('.modal-card-body').innerHTML = content;
        this.shadow.querySelector('.modal-card-foot .is-success').innerText = truthy;
        this.shadow.querySelector('.modal-card-foot .is-danger').innerText = falsy;
        this.shadow.querySelector('.modal').classList.add('is-active');
        return new Promise((resolve,reject)=>{
            this.shadow.querySelector('.modal-card-foot .is-success').addEventListener('click',()=>{
                resolve(true);
            });
            this.shadow.querySelector('.modal-card-foot .is-danger').addEventListener('click',()=>{
                resolve(false);
            });
        });
    }
    close(){
        this.shadow.querySelector('.modal').classList.remove('is-active');
    }
}
window.customElements.define('dialog-modal', DialogModal);
