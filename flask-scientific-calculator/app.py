from flask import Flask, request, jsonify, render_template_string
import math

app = Flask(__name__)

SAFE_FUNCTIONS = {
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "sqrt": math.sqrt,
    "log": math.log10,
    "ln": math.log,
    "pow": pow,
    "pi": math.pi,
    "e": math.e,
    "abs": abs,
    "round": round
}

def safe_eval(expr):
    try:
        result = eval(expr, {"__builtins__": None}, SAFE_FUNCTIONS)
        return str(result)
    except Exception:
        return "Error"

@app.route('/')
def home():
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Advanced Calculator</title>

<style>
body {
    margin: 0;
    font-family: 'Segoe UI';
    background: linear-gradient(135deg, #141e30, #243b55);
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
}
.container {
    display: flex;
    gap: 20px;
}
.calculator {
    backdrop-filter: blur(15px);
    background: rgba(255,255,255,0.1);
    padding: 20px;
    border-radius: 20px;
    box-shadow: 0 0 25px rgba(0,0,0,0.5);
    width: 320px;
}
.display {
    width: 100%;
    height: 60px;
    font-size: 24px;
    border-radius: 10px;
    border: none;
    padding: 10px;
    text-align: right;
    background: rgba(0,0,0,0.7);
    color: #00ffcc;
}
.buttons {
    display: grid;
    grid-template-columns: repeat(5,1fr);
    gap: 10px;
    margin-top: 15px;
}
button {
    padding: 15px;
    border-radius: 10px;
    border: none;
    background: rgba(255,255,255,0.1);
    color: white;
    cursor: pointer;
    transition: 0.2s;
}
button:hover {
    background: #00c9a7;
    transform: scale(1.05);
}
.equal {
    grid-column: span 2;
    background: #00c9a7;
    color: black;
}
.clear { background: #ff4b5c; }
.toggle {
    margin-top: 10px;
    text-align: center;
}
.history {
    width: 200px;
    background: rgba(0,0,0,0.5);
    padding: 10px;
    border-radius: 15px;
    color: white;
    overflow-y: auto;
    max-height: 400px;
}
.history h3 {
    text-align: center;
}
.history div {
    padding: 5px;
    border-bottom: 1px solid #444;
    cursor: pointer;
}
.light {
    background: #f2f2f2;
}
.light .calculator {
    background: white;
}
.light .display {
    background: #ddd;
    color: black;
}
.light button {
    background: #e0e0e0;
    color: black;
}
</style>
</head>

<body>

<div class="container">
<div class="calculator">
<input id="display" class="display" readonly>

<div class="buttons">
<button class="clear" onclick="clearDisplay()">C</button>
<button onclick="back()">←</button>
<button onclick="append('%')">%</button>
<button onclick="append('/')">/</button>
<button onclick="append('sqrt(')">√</button>

<button onclick="append('7')">7</button>
<button onclick="append('8')">8</button>
<button onclick="append('9')">9</button>
<button onclick="append('*')">*</button>
<button onclick="append('pow(')">pow</button>

<button onclick="append('4')">4</button>
<button onclick="append('5')">5</button>
<button onclick="append('6')">6</button>
<button onclick="append('-')">-</button>
<button onclick="append('ln(')">ln</button>

<button onclick="append('1')">1</button>
<button onclick="append('2')">2</button>
<button onclick="append('3')">3</button>
<button onclick="append('+')">+</button>
<button onclick="append('log(')">log</button>

<button onclick="append('(')">(</button>
<button onclick="append(')')">)</button>
<button onclick="append('0')">0</button>
<button onclick="append('.')">.</button>
<button class="equal" onclick="calculate()">=</button>
</div>

<div class="buttons">
<button onclick="append('sin(')">sin</button>
<button onclick="append('cos(')">cos</button>
<button onclick="append('tan(')">tan</button>
<button onclick="append('pi')">π</button>
<button onclick="append('e')">e</button>
</div>

<div class="toggle">
<button onclick="toggleTheme()">Theme</button>
<button onclick="toggleMode()">Deg/Rad</button>
</div>
</div>

<div class="history">
<h3>History</h3>
<div id="historyList"></div>
</div>

</div>

<script>
let isDegree = false;

function append(val){
    document.getElementById("display").value += val;
}

function clearDisplay(){
    document.getElementById("display").value = "";
}

function back(){
    let d = document.getElementById("display");
    d.value = d.value.slice(0,-1);
}

function toggleTheme(){
    document.body.classList.toggle("light");
}

function toggleMode(){
    isDegree = !isDegree;
    alert(isDegree ? "Degree Mode" : "Radian Mode");
}

function convertTrig(expr){
    if(!isDegree) return expr;
    return expr.replace(/(sin|cos|tan)\(([^)]+)\)/g, function(match, func, val){
        return func + "(" + val + "*Math.PI/180)";
    });
}

function calculate(){
    let expr = document.getElementById("display").value;
    expr = convertTrig(expr);

    fetch("/calculate", {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body: JSON.stringify({expression:expr})
    })
    .then(res=>res.json())
    .then(data=>{
        document.getElementById("display").value = data.result;
        addHistory(expr + " = " + data.result);
    });
}

function addHistory(item){
    let div = document.createElement("div");
    div.innerText = item;
    div.onclick = () => {
        document.getElementById("display").value = item.split("=")[0];
    };
    document.getElementById("historyList").prepend(div);
}

// Keyboard support
document.addEventListener("keydown", function(e){
    if("0123456789+-*/().".includes(e.key)){
        append(e.key);
    }
    if(e.key==="Enter") calculate();
    if(e.key==="Backspace") back();
});
</script>

</body>
</html>
""")

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    expr = data.get("expression", "")
    return jsonify({"result": safe_eval(expr)})

if __name__ == "__main__":
    app.run(debug=True)