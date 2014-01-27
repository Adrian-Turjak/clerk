
class { 'clerk': 
    hostname => '10.5.36.32',
}

exec { "apt-update":
    command => "/usr/bin/apt-get update"
}

Exec["apt-update"] -> Class['clerk']

