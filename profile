level = u[1]
xp = u[2]

if xp >= level * 100:
    level += 1
    xp = 0

return {
    "coins": u[0],
    "level": level,
    "xp": xp
}
