const BACKGROUNDCOLOR = ['#111114', 'whitesmoke']
const TEXTCOLOR = ['white', 'black']
const LINKCOLOR = ['orangered', 'blue']
let c = 0
document.getElementsByTagName("h1")[0].onclick = function () {
    document.body.style.backgroundColor = BACKGROUNDCOLOR[c % 2]
    document.getElementsByTagName("h1")[0].style.color = TEXTCOLOR[c % 2]
    document.getElementsByTagName("strong")[0].style.color = TEXTCOLOR[c % 2]
    let xx = document.getElementsByTagName("a")
    for (let i = 0; i < xx.length; i++) {
        xx[i].style.color = LINKCOLOR[c % 2]
    }
    c++
}