import logging as log
log.basicConfig(level=log.INFO)
from flask import Flask, render_template, request, abort, redirect, url_for, flash, jsonify, make_response
from flask_bootstrap import Bootstrap
from threaded_profiler import Profiler_Thread
from helper import prepare_df
import os
import datetime as dt
import pandas as pd
import json
import re
from reversed_proxy import ReverseProxied


app = Flask(__name__)
app.secret_key = str(hash(dt.datetime.now()))
bootstrap = Bootstrap(app)
app.wsgi_app = ReverseProxied(app.wsgi_app, script_name='/services/teepee/')
processes = {}

file_path = os.path.dirname(os.path.realpath(__file__))
meta_file = os.path.abspath(os.path.join(file_path, os.pardir)) + "/webapp/config/tpf_meta.json"
with open(meta_file) as f:
    tpf_meta = json.load(f)

file_path = os.path.dirname(os.path.realpath(__file__))
ns_file = os.path.abspath(os.path.join(file_path, os.pardir)) + "/webapp/config/namespace.json"
with open(ns_file) as f:
    namesspaces = json.load(f)


@app.route("/")
def index():
    return render_template("index.html", data={"name": "TPF Profiler"})

@app.route("/profiler", methods=["GET"])
def profiler():
    return render_template("profiler.html", data={"name": "TPF Profiler", "tpfs": tpf_meta})

@app.route("/config/namespaces", methods=["GET"])
def namespaces():
    return jsonify(namesspaces)

@app.route("/about", methods=["GET"])
def about():
    return render_template("about.html")

@app.route("/run", methods=["POST"])
def run():
    count = 0
    for process in processes.values():
        if not process.done:
            count += 1
    log.info("Currently running processes: {0}".format(count))
    if count >= 1:
        flash("Profiler currently running.")
        return redirect(url_for("profiler"))

    try:
        log.info(request.args.keys())
        uri = request.form['uri']
        samples_size = int(request.form['samples'])

        log.info(uri)
        log.info(samples_size)
        # id = abs(int(hash(str(dt.datetime.now()))))
        id = "U" + dt.datetime.now().strftime("%Y%m%d%H%M%S")
        meta_data = meta_by_uri(uri)
        p = Profiler_Thread(uri, samples_size, id, meta_data)
        p.start()

        processes[str(id)] = p
        return redirect(url_for("result", id=id))
    except Exception as e:
        log.exception(e)
        return abort(500)


@app.route("/result/status/<id>", methods=["GET"])
def result(id):
    if not str(id) in processes.keys(): return abort(404)
    p = processes[str(id)].progress
    status = "running"
    if p == 100: status = "done"
    log.info(request.headers['accept'])
    if "application/json" in request.headers['accept']:
        log.info("Status as JSON")
        data = {
            "id": id,
            "status": status,
            "progress": p
        }
        # log.info(data)
        return jsonify(data)

    else:
        p = processes[str(id)].progress
        log.info("Process: {0}; Status: {1}".format(str(id), p))
        return render_template("result.html", data={"status": status, "id": str(id), "progress": p})


@app.route("/result/data/<id>", methods=["GET"])
def data(id):
    file_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.abspath(os.path.join(file_path, os.pardir)) + "/webapp/results/{0}.csv".format(str(id))
    log.info("Filepath of csv file: {0}".format(file_path))
    if os.path.isfile(file_path):
        if "application/json" in request.headers['accept']:
            df = pd.read_csv(file_path)
            df = prepare_df(df)
            df.drop(['cached', 'study_id', 'vars', 'run', 'Unnamed: 0', 'page'], axis=1, inplace=True)
            json = df.to_json(orient='index')
            return jsonify(json)
        else:
            with open(file_path, 'r') as csv_file:
                csv_str = csv_file.read()
            response = make_response(csv_str)
            cd = 'attachment; filename=query_{0}.csv'.format(id)
            response.headers['Content-Disposition'] = cd
            response.mimetype = 'text/csv'
            return response
    else:
        log.info("Could not find CSV for job {0}".format(id))
        return abort(404)


@app.route("/result/visualize/<id>", methods=["GET"])
def visualize(id):
    jsoned = {
        "vals": csvfile_to_json(id),
        "meta": json_to_meta(id),
        "stats": get_stats(id)
    }
    log.info(jsoned)
    return render_template("visualization.html", data=jsoned)


@app.route("/result/visualize/links/<id>", methods=["GET"])
def get_flare(id):
    file_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.abspath(os.path.join(file_path, os.pardir)) + "/webapp/results/{0}.csv".format(str(id))
    log.info("Filepath of csv file: {0}".format(file_path))
    if os.path.isfile(file_path):
        df = pd.read_csv(file_path)
        df = prepare_df(df)
        vals = df['pattern'].values

        commons = {}
        for val in vals:
            elems = val[:-1].split(" ")

            for elem in elems:
                for val2 in vals:
                    elems2 = val2[:-1].split(" ")
                    if elem in elems2:
                        if elem != " ":
                            commons.setdefault(elem, set()).update(elems2)

        # log.info(commons)
        flare = []
        for elem, values in zip(commons.keys(), commons.values()):
            flare.append(
                {"name": add_namespace(elem),
                 "imports": [{'text': item, 'id': add_namespace(item)} for item in list(values)]
                 }
            )
        # log.info(flare)
        return jsonify(flare)


@app.route("/result/visualize/stats/<id>", methods=["GET"])
def stats(id):
    return jsonify(get_stats(id))


@app.route("/result/visualize/<id>/compare/<id2>", methods=["GET"])
def compare(id, id2):
    jsoned = {
        "a": csvfile_to_json(id),
        "b": csvfile_to_json(id2),
        "meta": {
            "a": json_to_meta(id),
            "b": json_to_meta(id2)
        },
        "stats": {
            "a": get_stats(id),
            "b": get_stats(id2)
        },
        "available": get_all_meta(),
        "aid": id,
        "bid": id2

    }
    # log.info(jsoned)
    return render_template("comparison.html", data=jsoned)


@app.route("/results/visualize/compare", methods=["GET"])
def compare_empty():
    empty_stats = {
        "Distinct subjects": 0,
        "Distinct predicates": 0,
        "Distinct objects": 0,
        "pattern_count": 0
    }
    jsoned = {
        "a": [],
        "b": [],
        "meta": {
            "a": [],
            "b": []
        },
        "available": get_all_meta(empty=True),
        "stats": {
            "a": empty_stats,
            "b": empty_stats
        },
    }
    # log.info(jsoned)
    return render_template("comparison.html", data=jsoned)


@app.route("/results", methods=["GET"])
def results():
    meta_path = os.path.dirname(os.path.realpath(__file__))
    meta_path = os.path.abspath(os.path.join(meta_path, os.pardir)) + "/webapp/results/meta/"

    results = []
    try:
        for meta_file in os.listdir(meta_path):
            if meta_file.endswith(".json"):
                with open(meta_path + meta_file) as f:
                    meta = json.load(f)
                    results.append(meta)

        # results = sorted(results, key= lambda x : x['id'])
        results = sorted(results, key=lambda e: ({int: 1, float: 1, str: 0}.get(type(e['id']), 0), e['id']))

    except Exception as e:
        log.info("Exception {0}".format(e))

    finally:
        log.info("Results: {0}".format(results))
        return render_template("results.html", data={"name": "Available Profiling Results", "data": results})


@app.route("/stop/<id>", methods=["GET"])
def kill_p(id):
    try:
        processes[str(id)].stop()
        flash("Stopped job: {0}".format(str(id)))
        return redirect(url_for("profiler"))

    except Exception as e:
        log.exception(e)
        return abort(400)


def csvfile_to_json(id):
    file_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.abspath(os.path.join(file_path, os.pardir)) + "/webapp/results/{0}.csv".format(str(id))
    log.info("Filepath of csv file: {0}".format(file_path))
    if os.path.isfile(file_path):
        df = pd.read_csv(file_path)
        df = prepare_df(df)
        df.drop(['cached', 'study_id', 'vars', 'run', 'Unnamed: 0', 'page'], axis=1, inplace=True)
        return df.to_dict(orient='index').values()
    else:
        log.info("Could not find CSV for job {0}".format(id))
        return []


def json_to_meta(id):
    meta_path = os.path.dirname(os.path.realpath(__file__))
    meta_file = os.path.abspath(os.path.join(meta_path, os.pardir)) + "/webapp/results/meta/{0}.json".format(id)

    if meta_file.endswith(".json"):
        with open(meta_file) as f:
            meta = json.load(f)
            return meta

    else:
        return {}


def get_all_meta(empty=False):
    meta_path = os.path.dirname(os.path.realpath(__file__))
    meta_path = os.path.abspath(os.path.join(meta_path, os.pardir)) + "/webapp/results/meta/"

    results = []
    if empty:
        empty_meta = {
            "id": "0",
            "uri": "-",
            "sample_size": "-",
            "backend": "-",
            "environment": "-"
        }
        results.append(empty_meta)

    try:
        for meta_file in os.listdir(meta_path):
            if meta_file.endswith(".json"):
                with open(meta_path + meta_file) as f:
                    meta = json.load(f)
                    results.append(meta)
    finally:
        results = sorted(results, key=lambda x: x['id'])
        return results


def meta_by_uri(uri):
    for elem in tpf_meta:
        if elem['uri'] == uri: return elem


def add_namespace(item):
    for namesspace, uri in zip(namesspaces.keys(), namesspaces.values()):
        if namesspace in item:
            item = item.replace(namesspace, uri + ":")
        elif "dbpedia" in item or "wiktionary" in item:
            rege = r'https?:\/\/(.*)\.dbpedia'
            res = re.findall(rege, item)
            if len(res) == 1:
                ns = "http://" + res[0] + ".dbpedia.org/resource/"
                prefix = "dbpedia-" + res[0]
                item = item.replace(ns, prefix + ":")
            else:
                rege = r'https?:\/\/(.*)\.wiktionary.org/wiki/'
                res = re.findall(rege, item)
                if len(res) == 1:
                    ns = "http://" + res[0] + ".wiktionary.org/wiki/"
                    prefix = "wiktionary-" + res[0]
                    item = item.replace(ns, prefix + ":")
                else:
                    rege = r'https?:\/\/(.*)\.wiktionary.org/w/'
                    res = re.findall(rege, item)
                    if len(res) == 1:
                        ns = "http://" + res[0] + ".wiktionary.org/wiki/"
                        prefix = "wiktionary-" + res[0]
                        item = item.replace(ns, prefix + ":")
    return item


def get_stats(id):
    file_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.abspath(os.path.join(file_path, os.pardir)) + "/webapp/results/{0}.csv".format(str(id))
    log.info("Filepath of csv file: {0}".format(file_path))
    if os.path.isfile(file_path):
        df = pd.read_csv(file_path)
        df = prepare_df(df)
        vals = df['pattern'].values

        subjects = set()
        predicates = set()
        objects = set()
        for val in vals:
            elems = val[:-1].split(" ")
            subjects.add(elems[0])
            predicates.add(elems[1])
            objects.add(elems[2])

        stats = {
            "Distinct subjects": len(subjects),
            "Distinct predicates": len(predicates),
            "Distinct objects": len(objects),
            "pattern_count": len(vals)
        }
        return stats
    else:
        return {}



if __name__ == '__main__':
    app.debug = True
    app.run(host="0.0.0.0", port=5055)
