from graph import build_graph
g = build_graph()
print('compile OK')
print('nodes:', list(g.get_graph().nodes))
print(g.get_graph().draw_ascii())