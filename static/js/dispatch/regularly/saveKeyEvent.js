document.addEventListener("keydown", saveKeyPress)

function saveKeyPress(e){
    if(e.keyCode === 113){
        let bus = ""
        let driver = ""
        for (i = 0; i < RouteListHBodyTr.length; i++){
            if(RouteListHBodyTr[i].children[0].children[0].checked){
                bus = RouteListHBodyTr[i].children[4].children[1].value
                let selecting = RouteListHBodyTr[i].children[5].children[0]
                let outsorcingSelecting = RouteListHBodyTr[i].children[6].children[0]
                if(selecting.options[selecting.selectedIndex].value !== "" && outsorcingSelecting.options[outsorcingSelecting.selectedIndex].value === ""){
                    driver = selecting.options[selecting.selectedIndex].value
                }else if(selecting.options[selecting.selectedIndex].value === "" && outsorcingSelecting.options[outsorcingSelecting.selectedIndex].value !== ""){
                    driver = outsorcingSelecting.options[selecting.selectedIndex].value
                }else if(selecting.options[selecting.selectedIndex].value === "" && outsorcingSelecting.options[outsorcingSelecting.selectedIndex].value === ""){
                    driver = ""
                }
            }
        };
        if(bus !== "" && driver !== ""){
            RouteList.submit();
        }else{
            alert("'차량'과 '운전원/용역'을 모두 선택해 주세요")
        }
    }
}

const dispatchSaveBtn = document.querySelector(".dispatchSaveBtn")

dispatchSaveBtn.addEventListener("click", dispatchSave)

function dispatchSave(){
    let bus = ""
    let driver = ""
    for (i = 0; i < RouteListHBodyTr.length; i++){
        if(RouteListHBodyTr[i].children[0].children[0].checked){
            bus = RouteListHBodyTr[i].children[4].children[1].value
            let selecting = RouteListHBodyTr[i].children[5].children[0]
            let outsorcingSelecting = RouteListHBodyTr[i].children[6].children[0]
            // if(selecting.options[selecting.selectedIndex].value !== "" && outsorcingSelecting.children.length <= 1){
            //     driver = selecting.options[selecting.selectedIndex].value
            // }else if(selecting.children.length <= 1 && outsorcingSelecting.options[outsorcingSelecting.selectedIndex].value !== ""){
            //     driver = outsorcingSelecting.options[selecting.selectedIndex].value
            // }
        }
    };
    if(bus !== "" && driver !== ""){
        RouteList.submit();
    }else{
        alert("'차량'과 '운전원/용역'을 모두 선택해 주세요")
    }
}