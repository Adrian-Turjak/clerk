
class artifice::api{
    include artifice::api::install
}

class artifice::api::install{
    package { 'python-keystoneclient':
      ensure => present,
      provider => 'pip',
      require => Package['python-pip'],
    }
    package { 'Flask':
      ensure => present,
      provider => 'pip',
      require => Package['python-pip'],
    }
    package { 'Flask-restful':
      ensure => present,
      provider => 'pip',
      require => Package['Flask'],
    }


}
