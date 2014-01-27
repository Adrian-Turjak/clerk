
class clerk::django{
    Class['clerk::django::python'] -> Class['clerk::django::install']
    include clerk::django::python
    include clerk::django::install
}

class clerk::django::python{
    package { 'python':
      ensure => present,
      before => Package['python-pip'],
    }
    package { 'python-pip':
      ensure => present,
      require => Package['python'],
    }  
}

class clerk::django::install{
    package { 'django':
      ensure => present,
      provider => 'pip',
      require => Package['python-pip'],
    }
    package { 'djangorestframework':
      ensure => present,
      provider => 'pip',
      require => Package['django'],
    }
    package { 'python-mysqldb':
      ensure => present,
    }
}
