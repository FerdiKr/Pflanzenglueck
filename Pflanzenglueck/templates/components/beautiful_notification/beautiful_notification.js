'use strict';


class BeautifulNotification extends HTMLElement {
    constructor(){
        super();
        this.shadow = this.attachShadow({mode: 'open'});
        this.shadow.innerHTML = `{% block html %}{% endblock %}`;
        this.notification = this.shadow.querySelector('.notification');
        this.closebutton = this.notification.querySelector('.delete');
        this.closebutton.addEventListener('click',()=>{this.close();});
        this.last_colorclass = undefined;
    }
    open(colorclass,content){
        this.notification.classList.add(colorclass);
        this.last_colorclass = colorclass;
        this.notification.querySelector('.content').innerHTML = content;
        this.shadow.querySelector('br').hidden = false;
        this.shadow.querySelector('.does-expand-contract').style.maxHeight = this.notification.scrollHeight + "px";
    }
    close(){
        this.shadow.querySelector('.does-expand-contract').style.maxHeight = null;
        setTimeout(()=>{
            this.shadow.querySelector('br').hidden = true;
            this.notification.classList.remove(this.last_colorclass);
        },200);
        
    }
}
window.customElements.define('beautiful-notification', BeautifulNotification);
