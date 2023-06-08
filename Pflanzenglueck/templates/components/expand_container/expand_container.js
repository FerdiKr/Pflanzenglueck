'use strict';


import {findInParents} from "/static/js/helpers.js";
class ExpandContainer extends HTMLElement {
    constructor(){
        super();
        this.expanded = false;
        this.shadow = this.attachShadow({mode: 'open'});
        this.shadow.innerHTML = `{% block html %}{% endblock %}`;
        this.expandcontainer = this.shadow.getElementById("expandcontainer");
        this.expandcontainer_inner = undefined;
        this.shadow.querySelector('slot').assignedElements().forEach(element=>{
            if(element.id==='expand_container_inner'){this.expandcontainer_inner=element;}
            else{
                let expandcontainer_inner = element.querySelector('table');
                if(expandcontainer_inner){this.expandcontainer_inner = expandcontainer_inner}
            }
        });
        this.expandcontainer_inner.style.display='block'
    }
    toggleExpansion(){
        if(this.expanded){
            this.contract();
        }
        else{
            this.expand();
        }
    }
    expand(){
        this.expandcontainer.style.maxHeight = this.expandcontainer.scrollHeight + "px";
        this.expandcontainer.style.height = this.expandcontainer.scrollHeight + "px";
        this.expanded = true;
    }
    contract(){
        this.expandcontainer.style.maxHeight = null;
        this.expandcontainer.style.height = null;
        this.expanded = false;
    }
}
window.customElements.define('expand-container', ExpandContainer);
