from core.physics import DESPAWN_AGE, STATIC_AGE, ParticlePool


def test_pool_spawn_activates_particle() -> None:
    pool = ParticlePool(capacity=2)

    particle = pool.spawn(1.0, 2.0, 3.0, block_type=1)

    assert particle is not None
    assert particle.active
    assert pool.active_count == 1


def test_pool_exhaustion_returns_none() -> None:
    pool = ParticlePool(capacity=1)

    assert pool.spawn(0.0, 0.0, 0.0, 1) is not None
    assert pool.spawn(0.0, 0.0, 0.0, 1) is None


def test_particle_gravity_decreases_z() -> None:
    pool = ParticlePool(capacity=1)
    particle = pool.spawn(1.0, 1.0, 5.0, 1)
    assert particle is not None
    particle.vx = 0.0
    particle.vy = 0.0
    particle.vz = 0.0

    pool.update()

    assert particle.vz < 0
    assert particle.z < 5.0


def test_particle_floor_bounce() -> None:
    pool = ParticlePool(capacity=1)
    particle = pool.spawn(1.0, 1.0, 0.2, 1)
    assert particle is not None
    particle.vz = -1.0

    pool.update()

    assert particle.z >= 0.0
    assert particle.vz > 0.0


def test_particle_becomes_static() -> None:
    pool = ParticlePool(capacity=1)
    particle = pool.spawn(1.0, 1.0, 1.0, 1)
    assert particle is not None
    particle.age = STATIC_AGE

    pool.update()

    assert particle.is_static


def test_particle_despawns_after_timeout() -> None:
    pool = ParticlePool(capacity=1)
    particle = pool.spawn(1.0, 1.0, 1.0, 1)
    assert particle is not None
    particle.age = DESPAWN_AGE

    pool.update()

    assert not particle.active
    assert pool.active_count == 0


def test_spawn_burst_count() -> None:
    pool = ParticlePool(capacity=20)

    spawned = pool.spawn_burst(0.0, 0.0, 0.0, block_type=1, count=4)

    assert 3 <= spawned <= 5
    assert pool.active_count == spawned


def test_clear_all() -> None:
    pool = ParticlePool(capacity=4)
    pool.spawn(0.0, 0.0, 0.0, 1)
    pool.spawn(0.0, 0.0, 0.0, 1)

    pool.clear_all()

    assert pool.active_count == 0
    assert len(pool.active_particles()) == 0


def test_clear_non_static_keeps_static_particles() -> None:
    pool = ParticlePool(capacity=3)
    moving = pool.spawn(0.0, 0.0, 0.0, 1)
    static = pool.spawn(0.0, 0.0, 0.0, 1)
    assert moving is not None
    assert static is not None
    static.is_static = True

    pool.clear_non_static()

    assert not moving.active
    assert static.active
    assert pool.active_count == 1
