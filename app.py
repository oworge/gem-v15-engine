    elif tab == "btts":
        html += '<div class="c"><div class="ct">✅ BTTS — Both Teams To Score</div>'
        for m in sorted(MATCHES, key=lambda x:x["btts_prob"], reverse=True):
            ev = edge(m["btts_odds"], m["btts_prob"])
            html += '<div class="mc"><div class="tt">' + m["home"] + ' vs ' + m["away"] + '</div>'
            html += '<div class="mm">' + m["league"] + '</div>'
            html += '<div class="mr"><div class="n">BTTS Yes</div><div class="o">' + str(m["btts_odds"]) + '</div><div class="p">' + str(int(m["btts_prob"]*100)) + '%</div><div class="ev">+' + str(ev) + '%</div></div></div>'
        html += '</div>'
    else:
        html += '<div class="c"><div class="ct">Tab: ' + tab + '</div><div>Working...</div></div>'
    
    html += '</div></body></html>'
    return html

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
