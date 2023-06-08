export async function PromiseBasedGetXHR(adress){
    return new Promise((resolve,reject)=>{
        const xhr = new XMLHttpRequest();
        xhr.open('GET',adress);
        xhr.send();
        xhr.onload = ()=>{
            resolve(xhr.responseText);
        }
        xhr.onerror = ()=>{
            reject(xhr.responseText);
        }
    });
}

export async function PromiseBasedPostXHR(adress,data){
    return new Promise((resolve,reject)=>{
        const xhr = new XMLHttpRequest();
        xhr.open('POST',adress);
        xhr.send(data);
        xhr.onload = ()=>{
            resolve(xhr.responseText);
        }
        xhr.onerror = ()=>{
            reject(xhr.responseText);
        }
    });
}

export function createIcon(prefandname){
    prefandname = prefandname.split(' ');
    return window.FontAwesome.icon({ prefix: prefandname[0], iconName: prefandname[1] }).html[0];
}

export function dateToTimestring(date){
    const day = ("0" + date.getDate()).slice(-2);
    const month = ("0" + (date.getMonth() + 1)).slice(-2);
    const year = date.getFullYear().toString();
    const hours = ("0" + date.getHours()).slice(-2);
    const minutes = ("0" + date.getMinutes()).slice(-2);
    const seconds = ("0" + date.getSeconds()).slice(-2);
    return `${day}.${month}.${year} ${hours}:${minutes}:${seconds}`;
}

export function isEmptyObject(obj){
    return obj && Object.keys(obj).length === 0 && Object.getPrototypeOf(obj) === Object.prototype;
}

export function findInParents(elem,tagname) {
    let parents = [];
    while(elem.parentNode && elem.parentNode.nodeName.toLowerCase() != 'body') {
        //console.log(elem)
        elem = elem.parentNode;
        if (elem.tagName===tagname){
            parents.push(elem);
        }
    }
    return parents;
}

/* findet alle Expandcontainer auf der Seite und...
-...lässt alle initial-expand-container beim Laden expanden
-...versieht alle inner-expand-container mit einem (einmaligen) eventlistener, damit sie beim ersten expanden ihre parents mit expanden
-...lässt alle expand-container beim Seitenabbau einklappen
*/
export function setupExpandContainers(nobeforeunload){
    if(typeof(nobeforeunload)==='undefined'){nobeforeunload = false;}
    window.customElements.whenDefined("expand-container").then(()=>{
        document.querySelectorAll('.initial-expand-container').forEach(expandcontainer=>expandcontainer.expand());
        document.querySelectorAll('.inner-expand-container').forEach(expandcontainer=>{
            expandcontainer.expandcontainer.addEventListener('transitionend', function reexpandparents() {
                expandcontainer.expandcontainer.removeEventListener('transitioned', reexpandparents);
                if(expandcontainer.expanded){
                    findInParents(expandcontainer.expandcontainer_inner,'EXPAND-CONTAINER').forEach(parentexpandcontainer=>{
                        parentexpandcontainer.expand();
                    });
                }
            });
        });
        if(!nobeforeunload){
            window.addEventListener("beforeunload", ()=>{
                document.querySelectorAll('expand-container').forEach(expandcontainer=>expandcontainer.contract());
            });
        }
    });
}

export function adjustParentExpandContainers(child){
    findInParents(child,'EXPAND-CONTAINER').forEach(parentexpandcontainer=>{
        parentexpandcontainer.contract();
        parentexpandcontainer.expand();
    });
}