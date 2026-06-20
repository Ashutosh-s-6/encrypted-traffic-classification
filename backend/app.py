from flask import Flask, render_template

app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static"
)

# =====================================================
# PAGE ROUTES
# =====================================================

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analytics")
def analytics():
    return render_template("analytics.html")


@app.route("/about-project")
def about_project():
    return render_template("about_project.html")


@app.route("/about-dataset")
def about_dataset():
    return render_template("about_dataset.html")


@app.route("/threat_intel")
def threat_intel():
    return render_template("threat_intel.html")


@app.route("/report")
def report():
    return render_template("report.html")


# =====================================================
# RUN SERVER
# =====================================================

if __name__ == "__main__":
    app.run(debug=True)